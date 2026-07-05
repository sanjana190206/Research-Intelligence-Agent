from rag.agents.base import AgentResult, BaseResearchAgent
from rag.granite_client import generate_text


class FutureTrendPredictionAgent(BaseResearchAgent):
    name = "Future Trend Prediction Agent"
    query = "future work emerging technologies datasets experiments opportunities"

    def run(self):
        context, evidence = self.get_context(n_results=7)
        prompt = f"""
You are the Future Trend Prediction Agent.

Use ONLY the research context to infer future directions. Frame all predictions as context-grounded recommendations.

Return EXACTLY this structure. Each section must have exactly 3 complete bullet points. Every bullet point must be a full, complete sentence.

Emerging Technologies:
1. <complete sentence>
2. <complete sentence>
3. <complete sentence>

Future Research Directions:
1. <complete sentence>
2. <complete sentence>
3. <complete sentence>

Suggested Datasets:
1. <complete sentence>
2. <complete sentence>
3. <complete sentence>

Suggested Experiments:
1. <complete sentence>
2. <complete sentence>
3. <complete sentence>

Research Opportunities:
1. <complete sentence>
2. <complete sentence>
3. <complete sentence>

Context:
{context}

Future Trend Prediction:
"""
        output = generate_text(prompt, max_new_tokens=800)
        return AgentResult(self.name, output, evidence, self.confidence_from_evidence(evidence))

