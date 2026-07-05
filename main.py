from rag.pdf_loader import extract_text
from rag.chunker import chunk_text
from rag.vector_store import store_chunks, search_chunks

text = extract_text("uploads/rp for agent.pdf")

chunks = chunk_text(text)

store_chunks(chunks)

query = "What is Artificial Intelligence?"

results = search_chunks(query)

documents = results

for i, doc in enumerate(documents, start=1):
    print(f"\n--- Result {i} ---\n")
    print(doc)