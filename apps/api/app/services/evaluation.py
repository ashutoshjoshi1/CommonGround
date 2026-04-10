from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models import Evaluation, EvaluationItem, EvaluationStatus, PromptVersion, Run
from app.services.query_runner import run_query_pipeline


def _bounded(value: float) -> float:
    return max(0.0, min(1.0, value))


def compute_item_scores(
    run: Run, citation_count: int, avg_retrieval_score: float
) -> dict[str, float]:
    groundedness = _bounded((citation_count / 3.0) * 0.7 + (0.3 if not run.abstained else 0.1))
    coverage = _bounded(citation_count / 4.0)
    retrieval_relevance = _bounded((avg_retrieval_score + 1) / 2)
    hallucination_risk = _bounded(1 - groundedness + (0.15 if citation_count == 0 else 0))
    return {
        "groundedness": groundedness,
        "citation_coverage": coverage,
        "retrieval_relevance": retrieval_relevance,
        "hallucination_risk": hallucination_risk,
    }


def run_evaluation(db: Session, evaluation: Evaluation) -> Evaluation:
    evaluation.status = EvaluationStatus.RUNNING
    db.commit()

    items = (
        db.query(EvaluationItem)
        .filter(EvaluationItem.evaluation_id == evaluation.id)
        .order_by(EvaluationItem.created_at.asc())
        .all()
    )

    passed = 0
    total_latency = 0
    scores = []

    for item in items:
        result = run_query_pipeline(
            db=db,
            workspace_id=evaluation.workspace_id,
            user_id=evaluation.created_by_id,
            query=item.query,
            prompt_version_id=evaluation.prompt_version_id,
            top_k=int(evaluation.config_json.get("top_k", 6)),
        )

        run = db.query(Run).filter(Run.id == result["run"].id).first()
        citations = result["citations"]
        avg_retrieval = (
            sum(c["score"] for c in citations) / max(1, len(citations)) if citations else 0.0
        )
        metric = compute_item_scores(
            run=run, citation_count=len(citations), avg_retrieval_score=avg_retrieval
        )

        item.run_id = run.id
        item.score_groundedness = metric["groundedness"]
        item.score_citation_coverage = metric["citation_coverage"]
        item.score_retrieval_relevance = metric["retrieval_relevance"]
        item.hallucination_risk = metric["hallucination_risk"]
        item.latency_ms = run.latency_ms
        threshold = float(evaluation.config_json.get("pass_threshold", 0.62))
        item.passed = metric["groundedness"] >= threshold and metric["hallucination_risk"] < 0.5
        item.notes = "Auto-evaluated"

        total_latency += run.latency_ms or 0
        passed += 1 if item.passed else 0
        scores.append(metric)

    evaluation.status = EvaluationStatus.COMPLETED
    evaluation.completed_at = datetime.now(UTC)
    evaluation.summary_json = {
        "items": len(items),
        "passed": passed,
        "pass_rate": round(passed / max(1, len(items)), 3),
        "avg_latency_ms": round(total_latency / max(1, len(items)), 2),
        "avg_groundedness": round(sum(s["groundedness"] for s in scores) / max(1, len(scores)), 3),
        "avg_hallucination_risk": round(
            sum(s["hallucination_risk"] for s in scores) / max(1, len(scores)), 3
        ),
    }
    db.commit()
    db.refresh(evaluation)
    return evaluation


def compare_prompt_versions(
    db: Session,
    evaluation: Evaluation,
    prompt_version_ids: list[str],
) -> list[dict]:
    comparison: list[dict] = []
    items = (
        db.query(EvaluationItem)
        .filter(EvaluationItem.evaluation_id == evaluation.id)
        .order_by(EvaluationItem.created_at.asc())
        .all()
    )

    for prompt_version_id in prompt_version_ids:
        pv = db.query(PromptVersion).filter(PromptVersion.id == prompt_version_id).first()
        if not pv:
            continue

        pass_count = 0
        total_groundedness = 0.0
        for item in items:
            result = run_query_pipeline(
                db=db,
                workspace_id=evaluation.workspace_id,
                user_id=evaluation.created_by_id,
                query=item.query,
                prompt_version_id=prompt_version_id,
                top_k=int(evaluation.config_json.get("top_k", 6)),
            )
            citations = result["citations"]
            avg_retrieval = (
                sum(c["score"] for c in citations) / max(1, len(citations)) if citations else 0.0
            )
            run = result["run"]
            metric = compute_item_scores(
                run=run, citation_count=len(citations), avg_retrieval_score=avg_retrieval
            )
            total_groundedness += metric["groundedness"]
            if metric["groundedness"] > 0.65 and metric["hallucination_risk"] < 0.5:
                pass_count += 1

        comparison.append(
            {
                "prompt_version_id": prompt_version_id,
                "model_name": pv.model_name,
                "provider": pv.provider,
                "pass_rate": round(pass_count / max(1, len(items)), 3),
                "avg_groundedness": round(total_groundedness / max(1, len(items)), 3),
            }
        )

    comparison.sort(key=lambda row: row["pass_rate"], reverse=True)
    return comparison
