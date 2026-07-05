from rag.agents.base import AgentResult, BaseResearchAgent
from rag.granite_client import generate_text


class LiteratureReviewAgent(BaseResearchAgent):
    name = "Literature Review Agent"
    query = "related work prior research literature methods findings limitations"

    def run(self):
        context, evidence = self.get_context(n_results=8)

        prompt = f"""
You are an expert research scientist.

Write a COMPLETE literature review.

Requirements:
- 800–1200 words.
- Finish every section.
- Never stop in the middle.
- Never return an incomplete sentence.
- Complete the entire review before ending.
- Use all relevant information from the research context.
- Finish every section completely.
- Do not stop until all sections are completed.

Sections:
1. Overview
2. Existing Research
3. Common Methodologies
4. Key Findings
5. Limitations
6. Research Gap
7. Relation to Uploaded Paper

Research Context:
{context}

Literature Review:
"""

        output = generate_text(prompt, max_new_tokens=1500)

        return AgentResult(
            self.name,
            output,
            evidence,
            self.confidence_from_evidence(evidence),
        )