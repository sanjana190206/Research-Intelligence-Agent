from rag.agents.section_drafting_agent import SectionDraftingAgent

def generate_section(section):
    return SectionDraftingAgent().run(section).output
