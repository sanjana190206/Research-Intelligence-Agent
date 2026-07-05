import re

def chunk_text(text, chunk_size=1200, overlap=200):
    """
    Split text into overlapping chunks while trying to preserve sentence boundaries.
    """

    text = re.sub(r"\s+", " ", text).strip()

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        if end < len(text):
            period = text.rfind(".", start, end)
            if period != -1:
                end = period + 1

        chunks.append(text[start:end].strip())

        start = end - overlap

    return chunks