import chromadb
from sentence_transformers import SentenceTransformer

COLLECTION_NAME = "professor_reviews"
CHROMA_PATH = "./chroma_db"

_model = None
_collection = None


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def _get_collection():
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        _collection = client.get_collection(COLLECTION_NAME)
    return _collection


def retrieve(query, top_k=5):
    model = _get_model()
    collection = _get_collection()

    query_embedding = model.encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for text, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append({
            "text": text,
            "source": meta["source"],
            "distance": round(dist, 4),
        })
    return chunks


if __name__ == "__main__":
    test_queries = [
        "What do students say about Professor Hart-Simmons' workload?",
        "Is Professor McGowan an easy class to pass?",
        "What do students think of Professor Poe's teaching style?",
    ]

    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 60)
        results = retrieve(query)
        for r in results:
            print(f"[dist={r['distance']}] ({r['source']})")
            print(r["text"])
            print()
