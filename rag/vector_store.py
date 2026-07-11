import chromadb

client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection("research_papers")


def store_chunks(chunks):
    print(f"Saving {len(chunks)} chunks")

    try:
        existing = collection.get()

        if existing.get("ids"):
            collection.delete(ids=existing["ids"])
            print("Old chunks deleted.")

    except Exception as e:
        print("Delete error:", e)

    ids = [str(i) for i in range(len(chunks))]

    collection.add(
        ids=ids,
        documents=chunks
    )

    print("Chunks stored successfully!")
    print("Collection count:", collection.count())


def search_chunks(query, n_results=3):
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    return results["documents"][0]


def search_chunks_with_scores(query, n_results=5):
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    documents = results["documents"][0]

    distances = results.get("distances", [[]])[0]

    evidence = []

    for i, doc in enumerate(documents):

        similarity = 1 - distances[i] if i < len(distances) else None

        evidence.append({
            "chunk": doc,
            "similarity_score": similarity,
        })

    return evidence


def get_all_chunks():
    data = collection.get()
    return data["documents"]