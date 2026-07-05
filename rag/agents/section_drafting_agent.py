from rag.agents.base import AgentResult, BaseResearchAgent
from rag.granite_client import generate_text


class SectionDraftingAgent(BaseResearchAgent):
    name = "Section Drafting Agent"
    query = "research paper introduction related work conclusion methodology"

    def run(self, section):
        context, evidence = self.get_context(f"{section} research paper section", n_results=7)
        prompt = f"""
You are the Section Drafting Agent.

Draft the {section} section directly using ONLY the context. Do not provide
instructions or meta commentary.

Context:
{context}

{section}:
"""
        output = generate_text(prompt, max_new_tokens=450)
        return AgentResult(self.name, output, evidence, self.confidence_from_evidence(evidence))

