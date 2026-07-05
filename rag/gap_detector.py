from rag.vector_store import collection
from rag.granite_client import generate_text

def detect_research_gaps():

    docs_raw = collection.get().get("documents", [])

    if docs_raw and isinstance(docs_raw[0], list):
        docs = [d for sub in docs_raw for d in sub]
    else:
        docs = docs_raw

    context = "\n\n".join(docs)

    prompt = f"""
You are a senior research analyst.

Analyze the paper and provide:

Research Gaps:
- point 1
- point 2
- point 3

Underexplored Areas:
- point 1
- point 2

Future Research Directions:
- point 1
- point 2


Potential Novel Contributions:
- point 1
- point 2

IMPORTANT:
- Use ONLY the provided context.
- Give specific findings.
- Do not explain what a research gap is.
- Do not repeat headings unnecessarily.
- Keep the answer concise.

Context:
{context}

Analysis:
"""

    return generate_text(prompt, max_new_tokens=400)
