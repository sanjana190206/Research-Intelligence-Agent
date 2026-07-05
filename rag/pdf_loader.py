from pypdf import PdfReader


def extract_text(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text


def extract_page_count(pdf_path: str) -> int:
    """Return the number of pages in a PDF."""
    try:
        return len(PdfReader(pdf_path).pages)
    except Exception:
        return 0


def extract_top_keywords(text: str, n: int = 5) -> list[str]:
    """Return the top-N meaningful keywords from the PDF text."""
    import re
    from collections import Counter

    STOP = {
        "the","and","for","that","with","this","from","are","was","were","has","have",
        "its","their","also","been","which","will","our","but","not","can","may","more",
        "than","such","both","each","when","where","how","what","these","those","use",
        "used","using","paper","show","shows","propose","proposed","method","model",
        "models","based","into","they","them","very","over","under","about","after",
        "before","while","other","between","within","through","being","here","there",
        "would","could","should","figure","table","section","therefore","however","thus",
        "results","result","study","data","research","analysis","approach","system",
    }
    tokens = re.findall(r"\b[a-z]{5,}\b", text.lower())
    freq = Counter(t for t in tokens if t not in STOP and t.isalpha())
    return [w.capitalize() for w, _ in freq.most_common(n * 3)
            if len(w) >= 5][:n]