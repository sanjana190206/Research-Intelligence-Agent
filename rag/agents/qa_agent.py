from rag.agents.base import AgentResult, BaseResearchAgent
from rag.granite_client import generate_text


class ResearchQAAgent(BaseResearchAgent):
    name = "Research Q&A Agent"

    def run(self, question, history=None):
        history = history or []
        context, evidence = self.get_context(question, n_results=5)
        recent_history = "\n".join(
            f"User: {item.get('question')}\nAssistant: {item.get('answer')}"
            for item in history[-4:]
        )
        prompt = f"""
You are the Research Q&A Agent.

Answer the user's question using ONLY the retrieved research context.
Use the conversation history only to understand follow-up references.
If the answer is not supported by the context, say that the uploaded paper context
does not contain enough evidence.

Conversation History:
{recent_history}

Retrieved Context:
{context}

Question:
{question}

Answer:
"""
        output = generate_text(prompt, max_new_tokens=512)
        return AgentResult(self.name, output, evidence, self.confidence_from_evidence(evidence))

