import chromadb

client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection("research_papers")

def store_chunks(chunks, source="uploaded_paper"):
    try:
        existing = collection.get()
        if existing.get("ids"):
            collection.delete(
                ids=existing["ids"]
            )
            print("Old chunks deleted.")
    except Exception:
        pass

    ids = [str(i) for i in range(len(chunks))]
    metadatas = [
        {
            "source": source,
            "chunk_index": i + 1,
        }
        for i in range(len(chunks))
    ]

    collection.add(
        ids=ids,
        documents=chunks,
        metadatas=metadatas,
    )

    print("Chunks stored successfully!")

def search_chunks(query, n_results=3):

    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    return results["documents"][0]


def search_chunks_with_scores(query, n_results=5):
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    evidence = []

    for index, document in enumerate(documents):
        distance = distances[index] if index < len(distances) else None
        similarity = None
        if distance is not None:
            similarity = max(0.0, min(1.0, 1.0 - float(distance)))

        evidence.append({
            "chunk": document,
            "similarity_score": similarity,
            "distance": distance,
            "source": metadatas[index].get("source", "uploaded_paper") if index < len(metadatas) and metadatas[index] else "uploaded_paper",
            "chunk_index": metadatas[index].get("chunk_index", index + 1) if index < len(metadatas) and metadatas[index] else index + 1,
        })

    return evidence


def get_all_chunks():
    data = collection.get()
    return data["documents"]
