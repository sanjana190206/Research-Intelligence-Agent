from dataclasses import dataclass, field
from typing import Any

from rag.vector_store import get_all_chunks, search_chunks_with_scores


@dataclass
class AgentResult:
    name: str
    output: Any
    evidence: list[dict[str, Any]] = field(default_factory=list)
    confidence_score: float = 0.0


class BaseResearchAgent:
    name = "Research Agent"
    query = "research paper"
    max_context_chunks = 10

    def get_context(self, query: str | None = None, n_results: int = 5):
        evidence = search_chunks_with_scores(query or self.query, n_results=n_results)
        context = "\n\n".join(item["chunk"] for item in evidence)
        return context, evidence

    def get_full_context(self):
        chunks = get_all_chunks()
        return "\n\n".join(chunks[: self.max_context_chunks])

    def confidence_from_evidence(self, evidence):
        scores = [
            item["similarity_score"]
            for item in evidence
            if item.get("similarity_score") is not None
        ]
        if not scores:
            return 0.55
        return round(sum(scores) / len(scores), 2)

