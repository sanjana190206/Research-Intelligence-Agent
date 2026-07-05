from rag.agents.qa_agent import ResearchQAAgent

def ask_question(question, history=None):
    return ResearchQAAgent().run(question, history).output

def ask_question_with_evidence(question, history=None):
    return ResearchQAAgent().run(question, history)
