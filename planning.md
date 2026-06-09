# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

Student reviews of professors at Grambling State University (GSU). This knowledge is valuable because official course catalogs describe what a class covers — not how hard it is, how a professor teaches, or whether students actually pass. Rate My Professors aggregates this informal student knowledge, but has no search or Q&A interface. Students cannot ask "which math professor is easiest?" or "what do students say about Professor X's exams?" and get a grounded, sourced answer. This RAG system makes that informal knowledge queryable.

---

## Documents

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Rate My Professors — Milisha Hart-Simmons | Math professor, 1.1★, 11 reviews | https://www.ratemyprofessors.com/professor/2406158 |
| 2 | Rate My Professors — Brian McGowan | History professor, 3.9★, 8 reviews | https://www.ratemyprofessors.com/professor/1498342 |
| 3 | Rate My Professors — Garry Poe | Information Science professor, 5.0★, 7 reviews | https://www.ratemyprofessors.com/professor/1577056 |
| 4 | Rate My Professors — Gertrude Roebuck | Math professor, 4.3★, 5 reviews | https://www.ratemyprofessors.com/professor/711283 |
| 5 | Rate My Professors — James Clawson | English professor, 4.0★, 5 reviews | https://www.ratemyprofessors.com/professor/1866988 |
| 6 | Rate My Professors — Mica Gould | Humanities professor, 4.9★, 4 reviews | https://www.ratemyprofessors.com/professor/1287098 |
| 7 | Rate My Professors — Charles Snodgrass | English professor, 2.5★, 4 reviews | https://www.ratemyprofessors.com/professor/2293302 |
| 8 | Rate My Professors — Frederick Semwogerere | Math professor, 3.7★, 3 reviews | https://www.ratemyprofessors.com/professor/1846752 |
| 9 | Rate My Professors — Marcus Davis | Social Science professor, 4.7★, 3 reviews | https://www.ratemyprofessors.com/professor/2358851 |
| 10 | Rate My Professors — Lee Britt | Physics professor, 4.7★, 3 reviews | https://www.ratemyprofessors.com/professor/1846779 |

---

## Chunking Strategy

**Chunk size:** 200 characters

**Overlap:** 50 characters

**Reasoning:**
The documents are short student reviews — typically 1 to 3 sentences per review, ranging from 50 to 150 words each. A 200-character chunk is large enough to hold one complete opinion or observation without cutting off mid-thought, but small enough that a single chunk does not blend opinions about multiple topics (e.g., workload and grading style) into one embedding. Using 500-character chunks on this corpus would merge multiple reviews into a single chunk, diluting the semantic signal and making it harder to retrieve the specific opinion a query is looking for.

Overlap of 50 characters ensures that a sentence split across a chunk boundary is represented in both adjacent chunks, so a complete thought is always retrievable even if it falls near an edge.

No preprocessing beyond what was done during document collection is needed — the `.txt` files are already clean plain text with no HTML, navigation menus, or boilerplate.

---

## Retrieval Approach

**Embedding model:** `all-MiniLM-L6-v2` via `sentence-transformers`

**Top-k:** 5

**Production tradeoff reflection:**
For a real deployment, the main tradeoffs when choosing a different embedding model would be:
- **Accuracy on informal text:** `all-MiniLM-L6-v2` is a general-purpose model trained on diverse web text, which includes informal reviews. A domain-fine-tuned model (e.g., one trained specifically on student feedback or educational text) could improve retrieval quality for slang and abbreviations common in student reviews.
- **Context length:** `all-MiniLM-L6-v2` has a 256-token limit, which is fine for short review chunks but would be a bottleneck for longer documents.
- **Latency vs. accuracy:** Larger models like `text-embedding-3-large` (OpenAI) produce higher-quality embeddings but add API latency and per-call cost. For a low-traffic internal tool, that tradeoff might be worth it; for a high-traffic app, local inference with `all-MiniLM-L6-v2` is more practical.
- **Multilingual support:** Not a concern for this corpus, but would matter if reviews were in multiple languages.

---

## Evaluation Plan

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What do students say about Professor Hart-Simmons' workload? | Over 30 tasks in a 4-week course, work due daily, overwhelming workload especially in summer sessions |
| 2 | Is Professor McGowan an easy class to pass? | Yes — show up, take notes, and you will get an A; grading is based on attendance and a few exams |
| 3 | What do students think of Professor Poe's teaching style? | He is a great professor who pushes students hard but teaches well and makes sure students understand; 100% of reviewers would take him again |
| 4 | Which English professors at GSU do students recommend? | Mica Gould (4.9★) and James Clawson (4.0★) are both recommended; Charles Snodgrass is more mixed |
| 5 | What are the main complaints students have about Professor Hart-Simmons? | Unresponsive to emails, excessive and repetitive assignments, delayed grading, poor communication, and a heavy workload compressed into short time frames |

---

## Anticipated Challenges

1. **Thin corpus — too few chunks for reliable retrieval.** With ~58 reviews across 10 professors, the total text volume is small. If chunks are too large, the total chunk count may fall below 50, which means retrieval has little to distinguish between. This will be mitigated by using small chunk sizes (200 characters), but retrieval quality may still be weaker than a larger corpus.

2. **Professor name matching.** Students on RMP often refer to professors by last name only, first name only, or nicknames (e.g., "Dr. Poe", "McGowan", "Ms. Roebuck"). If a query uses a different form of the name than what appears in the chunks, the embedding may not match well. For example, a query for "Garry Poe" may not retrieve a review that only says "Dr. Poe." This is a known limitation of semantic search on short, name-heavy text.

---

## Architecture

```
+------------------+       +------------------+       +-------------------------+
|  Document        |       |   Chunking        |       |  Embedding +            |
|  Ingestion       +-----> |   (chunk_text)    +-----> |  Vector Store           |
|                  |       |                   |       |                         |
|  Tool: Python    |       |  Tool: Python     |       |  Tool: sentence-        |
|  (open / read    |       |  (character split,|       |  transformers           |
|   .txt files)    |       |   size=200,       |       |  (all-MiniLM-L6-v2)     |
|                  |       |   overlap=50)     |       |  + ChromaDB             |
+------------------+       +------------------+       +----------+--------------+
                                                                  |
                                                                  v
+------------------+       +---------------------------+----------+--------------+
|  Generation      |       |  Retrieval                                          |
|                  | <---  |                                                      |
|  Tool: Groq API  |       |  Tool: ChromaDB similarity search                   |
|  (llama-3.3-70b- |       |  top-k = 5                                          |
|   versatile)     |       |                                                      |
|                  |       |                                                      |
|  Interface:      |       |                                                      |
|  Gradio          |       |                                                      |
+------------------+       +--------------------------------------------------+
```

---

## AI Tool Plan

**Milestone 3 — Ingestion and chunking:**
I will give Claude the Documents section (file names and format of the `.txt` files) and the Chunking Strategy section of this planning.md. I will ask it to implement two functions: `load_documents()` that reads all `.txt` files from the `documents/` folder and returns a list of dicts with `text` and `source` fields, and `chunk_text()` that splits a string into chunks of 200 characters with 50-character overlap. I will verify the output by printing 5 sample chunks and checking that each is readable and self-contained.

**Milestone 4 — Embedding and retrieval:**
I will give Claude the Retrieval Approach section and the Architecture diagram. I will ask it to implement `embed_and_store()` that takes the chunked documents, embeds them with `all-MiniLM-L6-v2`, and stores them in a ChromaDB collection with `source` metadata, and a `retrieve()` function that accepts a query string and returns the top-5 most relevant chunks with their source filenames. I will verify by running 3 of my evaluation plan queries and checking that the returned chunks visibly relate to each question.

**Milestone 5 — Generation and interface:**
I will give Claude the grounding requirement (answer only from retrieved context, cite sources) and the Gradio skeleton from the project instructions. I will ask it to implement the `ask()` function that calls `retrieve()`, formats the chunks as context, sends them to the Groq API with a grounding system prompt, and returns the answer plus source list. I will verify by asking a question my documents don't cover and confirming the system declines to answer rather than hallucinating.
