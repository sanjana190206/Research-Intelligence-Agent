from rag.agents.qa_agent import ResearchQAAgent


def ask_question_with_evidence(question, history=None):
    agent = ResearchQAAgent()
    return agent.run(question, history)