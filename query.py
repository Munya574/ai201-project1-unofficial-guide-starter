import os
from groq import Groq
from dotenv import load_dotenv
from retrieve import retrieve

load_dotenv()

SYSTEM_PROMPT = """You are a helpful assistant that answers questions about professors at Grambling State University based solely on student reviews.

Rules:
- Answer using ONLY the information in the student reviews provided below.
- Always cite which source document(s) your answer draws from (e.g. "According to rmp_poe_infoscience.txt...").
- If the reviews do not contain enough information to answer the question, respond with exactly: "I don't have enough information in the available reviews to answer that."
- Never use knowledge from outside the provided reviews, even if you know the answer."""


def ask(question):
    chunks = retrieve(question)

    context = "\n\n".join(
        f"[Source: {c['source']}]\n{c['text']}"
        for c in chunks
    )

    user_message = f"Student reviews:\n{context}\n\nQuestion: {question}"

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2,
    )

    answer = response.choices[0].message.content
    # Deduplicate sources while preserving order
    seen = set()
    sources = []
    for c in chunks:
        if c["source"] not in seen:
            seen.add(c["source"])
            sources.append(c["source"])

    return {"answer": answer, "sources": sources}


if __name__ == "__main__":
    # Grounding test — ask something the documents don't cover
    out_of_scope = ask("What are the best restaurants near Grambling State University?")
    print("=== Out-of-scope query (should decline) ===")
    print(out_of_scope["answer"])
    print()

    # On-topic test
    on_topic = ask("What do students say about Professor Poe?")
    print("=== On-topic query ===")
    print(on_topic["answer"])
    print("\nSources:", on_topic["sources"])
