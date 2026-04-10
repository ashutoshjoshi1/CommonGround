from __future__ import annotations

from dataclasses import dataclass

from app.services.retrieval import RetrievedPassage


@dataclass
class RAGResult:
    answer: str
    confidence_label: str
    abstained: bool


def render_prompt(prompt_template: str, query: str, passages: list[RetrievedPassage]) -> str:
    context = "\n\n".join(
        f"[{idx + 1}] {p.source.file_name}: {p.chunk.content[:600]}"
        for idx, p in enumerate(passages)
    )
    return (
        f"{prompt_template}\n\n"
        f"Query:\n{query}\n\n"
        f"Retrieved Context:\n{context}\n\n"
        "Write findings grounded in cited context."
    )


def build_grounded_answer(query: str, passages: list[RetrievedPassage]) -> RAGResult:
    if not passages:
        return RAGResult(
            answer=(
                "No grounded answer could be produced from the current workspace sources. "
                "Add relevant documents or broaden the query scope and retry."
            ),
            confidence_label="low",
            abstained=True,
        )

    top_score = passages[0].score
    if top_score < 0.18:
        return RAGResult(
            answer=(
                "Available evidence is weak for this question. "
                "I am withholding a definitive answer until stronger source support is available."
            ),
            confidence_label="review",
            abstained=True,
        )

    summary_lines = []
    for idx, passage in enumerate(passages[:3], start=1):
        snippet = passage.chunk.content.replace("\n", " ").strip()
        summary_lines.append(f"[{idx}] {snippet[:280]}")

    answer = "Based on the retrieved workspace evidence, key findings are:\n" + "\n".join(
        f"- {line}" for line in summary_lines
    )

    confidence = "high" if top_score >= 0.45 else "review"
    return RAGResult(answer=answer, confidence_label=confidence, abstained=False)
