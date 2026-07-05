from rag.agents.summarization_agent import ResearchSummarizationAgent

def summarize_paper():
    return ResearchSummarizationAgent().run().output
