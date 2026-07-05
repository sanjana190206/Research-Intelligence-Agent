from rag.agents.base import AgentResult, BaseResearchAgent
from rag.granite_client import generate_text


class ResearchSummarizationAgent(BaseResearchAgent):
    name = "Research Summarization Agent"
    query = "paper summary problem methodology dataset results limitations"

    def run(self):
        context, evidence = self.get_context(n_results=8)
        prompt = f"""
You are an expert academic research summarizer.

Using ONLY the research context below, produce a complete research summary.

Requirements:
- Include ALL sections.
- Complete every section before ending.
- Never stop in the middle of a sentence.
- Do not invent information not present in the context.
- Use professional academic language.

Return exactly these headings:

 1.Topic

 2.Problem Statement

 3.Methodology

 4.Dataset or Evidence Base

 5.Key Results

 6.Limitations


Context:
{context}

Summary:
"""
        output = generate_text(prompt, max_new_tokens=800)
        return AgentResult(self.name, output, evidence, self.confidence_from_evidence(evidence))

