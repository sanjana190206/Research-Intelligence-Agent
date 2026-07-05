from rag.agents.base import AgentResult, BaseResearchAgent
from rag.granite_client import generate_text


class HypothesisGenerationAgent(BaseResearchAgent):
    name = "Hypothesis Generation Agent"
    query = "research gaps hypothesis future work experiment"

    def run(self):
        context, evidence = self.get_context(n_results=7)
        prompt = f"""
You are the Hypothesis Generation Agent.

Based only on the context, identify gaps and generate 3 testable hypotheses.
For each hypothesis include rationale, variables, and a validation idea.

Context:
{context}

Hypotheses:
"""
        output = generate_text(prompt, max_new_tokens=400)
        return AgentResult(self.name, output, evidence, self.confidence_from_evidence(evidence))

