from __future__ import annotations

from datetime import UTC, datetime
from time import perf_counter

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import PromptVersion, RetrievedChunk, Run, RunStatus, RunStep
from app.services.rag import build_grounded_answer
from app.services.retrieval import RetrievalService

retrieval_service = RetrievalService()


def _resolve_prompt_template(db: Session, prompt_version_id: str | None) -> tuple[str, str | None]:
    if prompt_version_id:
        prompt_version = (
            db.query(PromptVersion).filter(PromptVersion.id == prompt_version_id).first()
        )
        if prompt_version:
            return prompt_version.template, prompt_version.id

    default_prompt = (
        db.query(PromptVersion)
        .filter(PromptVersion.is_default.is_(True))
        .order_by(PromptVersion.created_at.desc())
        .first()
    )
    if default_prompt:
        return default_prompt.template, default_prompt.id

    return (
        "Answer with grounded evidence. If evidence is weak, abstain and state why.",
        None,
    )


def run_query_pipeline(
    db: Session,
    *,
    workspace_id: str,
    user_id: str,
    query: str,
    prompt_version_id: str | None,
    top_k: int | None,
) -> dict:
    started = perf_counter()
    template, resolved_prompt_id = _resolve_prompt_template(db, prompt_version_id)

    run = Run(
        workspace_id=workspace_id,
        user_id=user_id,
        prompt_version_id=resolved_prompt_id,
        query=query,
        status=RunStatus.RUNNING,
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    retrieval_start = perf_counter()
    passages = retrieval_service.retrieve(
        db=db,
        workspace_id=workspace_id,
        query=query,
        top_k=top_k or settings.default_top_k,
    )
    retrieval_duration = int((perf_counter() - retrieval_start) * 1000)

    db.add(
        RunStep(
            run_id=run.id,
            step_name="retrieve",
            step_order=1,
            status="completed",
            input_json={"query": query, "top_k": top_k or settings.default_top_k},
            output_json={"matches": len(passages)},
            duration_ms=retrieval_duration,
        )
    )

    rag_start = perf_counter()
    rag_result = build_grounded_answer(query=query, passages=passages)
    rag_duration = int((perf_counter() - rag_start) * 1000)

    db.add(
        RunStep(
            run_id=run.id,
            step_name="synthesize",
            step_order=2,
            status="completed",
            input_json={"prompt": template[:500]},
            output_json={"abstained": rag_result.abstained},
            duration_ms=rag_duration,
        )
    )

    citations: list[dict] = []
    for passage in passages:
        citation_label = f"S{passage.rank}"
        excerpt = passage.chunk.content[:500]
        citations.append(
            {
                "citation_label": citation_label,
                "source_id": passage.source.id,
                "source_name": passage.source.file_name,
                "chunk_id": passage.chunk.id,
                "rank": passage.rank,
                "score": round(passage.score, 4),
                "excerpt": excerpt,
            }
        )
        db.add(
            RetrievedChunk(
                run_id=run.id,
                source_chunk_id=passage.chunk.id,
                rank=passage.rank,
                score=float(passage.score),
                citation_label=citation_label,
                excerpt=excerpt,
            )
        )

    run.answer = rag_result.answer
    run.status = RunStatus.COMPLETED
    run.abstained = rag_result.abstained
    run.confidence_label = rag_result.confidence_label
    run.provider = "local"
    run.model_name = "grounded-extractive"
    run.usage_json = {"prompt_chars": len(query), "retrieved_chunks": len(passages)}
    run.latency_ms = int((perf_counter() - started) * 1000)
    run.completed_at = datetime.now(UTC)

    db.commit()
    db.refresh(run)

    return {
        "run": run,
        "citations": citations,
        "trace": {
            "retrieval_duration_ms": retrieval_duration,
            "synthesis_duration_ms": rag_duration,
            "prompt_version_id": resolved_prompt_id,
        },
    }
