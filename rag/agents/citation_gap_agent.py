from rag.agents.base import AgentResult, BaseResearchAgent
from rag.granite_client import generate_text


class CitationGapDetectionAgent(BaseResearchAgent):
    name = "Citation Gap Detection Agent"
    query = "references citations related work recent papers missing topics"

    def run(self):
        context, evidence = self.get_context(n_results=8)
        prompt = f"""
You are the Citation Gap Detection Agent.

Analyze the uploaded paper context and identify citation gaps.
Use ONLY the provided context. Do not invent paper titles; recommend the type of research area or paper that should be cited.

Return EXACTLY this structure. Each section must have exactly 3 complete bullet points. Every bullet point must be a full, complete sentence.

Missing References or Source Types:
1. <complete sentence>
2. <complete sentence>
3. <complete sentence>

Recent Papers or Areas That Should Be Cited:
1. <complete sentence>
2. <complete sentence>
3. <complete sentence>

Missing Research Topics:
1. <complete sentence>
2. <complete sentence>
3. <complete sentence>

Why Each Recommendation Is Useful:
1. <complete sentence>
2. <complete sentence>
3. <complete sentence>

Context:
{context}

Citation Gap Analysis:
"""
        output = generate_text(prompt, max_new_tokens=700)
        return AgentResult(self.name, output, evidence, self.confidence_from_evidence(evidence))

