"""Extract and format references/citations found in the uploaded paper chunks."""
import re
from rag.vector_store import get_all_chunks
from rag.granite_client import generate_text


def extract_references() -> dict:
    """Return a list of detected citations and a BibTeX-style string."""
    chunks = get_all_chunks()
    if not chunks:
        return {"references": [], "bibtex": ""}

    # Heuristic: find chunks that look like reference sections
    ref_chunks = []
    for chunk in chunks:
        lower = chunk.lower()
        if any(marker in lower for marker in ["references", "bibliography", "works cited", "[1]", "[2]", "et al."]):
            ref_chunks.append(chunk)

    context = "\n\n".join(ref_chunks[:6]) if ref_chunks else "\n\n".join(chunks[:4])

    prompt = f"""You are a reference extraction agent.

Extract up to 15 references from the text below.
Return them as a numbered list. Each entry must be one line in this format:
[N] Author(s). Title. Venue, Year.

If you cannot determine a field, write Unknown.
Do NOT invent references that are not present in the text.

Text:
{context}

References:
"""
    raw = generate_text(prompt, max_new_tokens=600)

    # Parse into structured list
    refs = []
    for line in raw.splitlines():
        m = re.match(r"\[(\d+)\]\s+(.+)", line.strip())
        if m:
            refs.append({"number": int(m.group(1)), "citation": m.group(2).strip()})

    # Build simple BibTeX
    bibtex_lines = []
    for ref in refs:
        key = f"ref{ref['number']}"
        bibtex_lines.append(f"@misc{{{key},\n  note = {{{ref['citation']}}}\n}}")
    bibtex = "\n\n".join(bibtex_lines)

    return {"references": refs, "bibtex": bibtex, "raw": raw}
