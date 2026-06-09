import os


def load_documents(folder="documents"):
    docs = []
    for filename in sorted(os.listdir(folder)):
        if not filename.endswith(".txt"):
            continue
        path = os.path.join(folder, filename)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        # Strip file header (everything before the first "---" separator)
        # so only review text gets chunked, not metadata like URLs and ratings
        if "---" in text:
            text = text[text.index("---") + 3:].strip()
        docs.append({"text": text, "source": filename})
    return docs


def chunk_text(text, chunk_size=200, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        chunk = text[start : start + chunk_size]
        if chunk.strip():
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def _professor_name(filename):
    # Derive a readable professor name from the filename for chunk prepending
    # e.g. "rmp_hart_simmons_math.txt" -> "Professor Hart Simmons"
    name_part = filename.replace("rmp_", "").rsplit("_", 1)[0]
    return "Professor " + name_part.replace("_", " ").title()


def chunk_documents(docs, chunk_size=200, overlap=50):
    chunked = []
    for doc in docs:
        prefix = _professor_name(doc["source"]) + ": "
        chunks = chunk_text(doc["text"], chunk_size, overlap)
        for i, chunk in enumerate(chunks):
            chunked.append({
                "text": prefix + chunk,
                "source": doc["source"],
                "chunk_index": i,
            })
    return chunked


if __name__ == "__main__":
    docs = load_documents()
    print(f"Loaded {len(docs)} documents\n")

    all_chunks = chunk_documents(docs)
    print(f"Total chunks: {len(all_chunks)}\n")

    print("--- 5 sample chunks ---\n")
    step = max(1, len(all_chunks) // 5)
    samples = [all_chunks[i * step] for i in range(5)]
    for i, chunk in enumerate(samples, 1):
        print(f"[Chunk {i}] source={chunk['source']} index={chunk['chunk_index']}")
        print(chunk["text"])
        print()
