import chromadb
from sentence_transformers import SentenceTransformer
from ingest import load_documents, chunk_documents

COLLECTION_NAME = "professor_reviews"
CHROMA_PATH = "./chroma_db"


def embed_and_store():
    docs = load_documents()
    chunks = chunk_documents(docs)
    print(f"Embedding {len(chunks)} chunks...")

    model = SentenceTransformer("all-MiniLM-L6-v2")
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True).tolist()

    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # Drop and recreate so re-runs start clean
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = client.create_collection(
        COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
    )
    collection.add(
        ids=[f"{c['source']}__{c['chunk_index']}" for c in chunks],
        embeddings=embeddings,
        documents=texts,
        metadatas=[{"source": c["source"], "chunk_index": c["chunk_index"]} for c in chunks],
    )

    print(f"Stored {collection.count()} chunks in '{COLLECTION_NAME}'")
    return collection


if __name__ == "__main__":
    embed_and_store()
