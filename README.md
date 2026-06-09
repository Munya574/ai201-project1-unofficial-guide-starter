# The Unofficial Guide — Project 1

---

## Domain

Student reviews of professors at Grambling State University (GSU). This knowledge is valuable because official course catalogs describe what a class covers — not how hard it is, how a professor teaches, or whether students actually pass. Rate My Professors aggregates this informal student knowledge but has no search or Q&A interface. Students cannot ask "which math professor is easiest?" or "what do students say about Professor X's workload?" and get a grounded, sourced answer. This RAG system makes that informal knowledge queryable.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Rate My Professors — Milisha Hart-Simmons | Web (copied to .txt) | https://www.ratemyprofessors.com/professor/2406158 |
| 2 | Rate My Professors — Brian McGowan | Web (copied to .txt) | https://www.ratemyprofessors.com/professor/1498342 |
| 3 | Rate My Professors — Garry Poe | Web (copied to .txt) | https://www.ratemyprofessors.com/professor/1577056 |
| 4 | Rate My Professors — Gertrude Roebuck | Web (copied to .txt) | https://www.ratemyprofessors.com/professor/711283 |
| 5 | Rate My Professors — James Clawson | Web (copied to .txt) | https://www.ratemyprofessors.com/professor/1866988 |
| 6 | Rate My Professors — Mica Gould | Web (copied to .txt) | https://www.ratemyprofessors.com/professor/1287098 |
| 7 | Rate My Professors — Charles Snodgrass | Web (copied to .txt) | https://www.ratemyprofessors.com/professor/2293302 |
| 8 | Rate My Professors — Frederick Semwogerere | Web (copied to .txt) | https://www.ratemyprofessors.com/professor/1846752 |
| 9 | Rate My Professors — Marcus Davis | Web (copied to .txt) | https://www.ratemyprofessors.com/professor/2358851 |
| 10 | Rate My Professors — Lee Britt | Web (copied to .txt) | https://www.ratemyprofessors.com/professor/1846779 |

---

## Chunking Strategy

**Chunk size:** 200 characters

**Overlap:** 50 characters

**Why these choices fit your documents:**
The documents are short student reviews — typically 1 to 3 sentences each, ranging from 50 to 150 words. A 200-character chunk is large enough to hold one complete opinion without cutting off mid-thought, but small enough that a single chunk does not blend opinions about multiple topics into one embedding. Using larger chunks (e.g., 500 characters) on this corpus would merge multiple reviews together and dilute the semantic signal, making it harder to retrieve the specific opinion a query is looking for. An overlap of 50 characters ensures that a sentence split across a chunk boundary is represented in both adjacent chunks, so a complete thought is always retrievable even if it falls near an edge.

Each `.txt` file has a header section (professor name, department, overall rating, source URL) separated from the review text by a `---` delimiter. The loader strips the header before chunking so that only review content is embedded — this prevents chunks like partial URLs from polluting the vector store.

Each chunk also has the professor's name prepended (e.g., `"Professor Hart Simmons: ..."`) before embedding. Without this, reviews that use pronouns like "she" or "this professor" cannot be retrieved by queries that mention the professor by name — a known limitation of semantic search on short review text.

**Final chunk count:** 53 chunks across 10 documents

**Sample chunks:**

1. `rmp_hart_simmons_math.txt` (chunk 3):
   > Professor Hart Simmons: ported her to the dean. — Course: MATH147 | Date: Oct 13, 2025 | Grade: F — This professor assigned over 30 tasks in a 4-week course, with work due daily except weekends. She gave little support, wa

2. `rmp_mcgowan_history.txt` (chunk 0):
   > Professor Mcgowan: Course: HIST102 | Date: Sep 18, 2025 | Grade: A — One of the best professors I have ever had. He talks a lot during lectures but is funny and entertaining. Has very few grades just attendance and exams

3. `rmp_poe_infoscience.txt` (chunk 2):
   > Professor Poe: Course: CIS215 | Date: Jan 2026 — Best professor ever. I like how he teaches, and the work is work but he teaches it well and makes sure you understand it. — Course: CIS371 | Date: Nov 2025 — Great pr

4. `rmp_gould_humanities.txt` (chunk 0):
   > Professor Gould: Course: ENG200 | Date: Jan 18, 2019 | Grade: A+ — She is the best of the best. If you want a straight A then go for her. Attendance is mandatory but her lectures are amazing.

5. `rmp_clawson_english.txt` (chunk 1):
   > Professor Clawson: I took him multiple semesters. He is a great teacher if you want to actually learn something. You will have to work and be very attentive in his class.

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers`. This model runs locally with no API key and no rate limits, which makes it practical for development. It was pre-trained on a large and diverse web corpus including informal text, making it reasonable for short opinion-based reviews.

**Production tradeoff reflection:**
For a real deployment, the main tradeoffs when choosing a different model would be: (1) **Accuracy on informal text** — a domain-fine-tuned model trained on student feedback or educational text could improve retrieval quality for slang and abbreviations common in reviews; (2) **Context length** — `all-MiniLM-L6-v2` has a 256-token limit, which is fine for 200-character chunks but would be a bottleneck for longer documents; (3) **Latency vs. accuracy** — larger hosted models like OpenAI's `text-embedding-3-large` produce higher-quality embeddings but add API latency and per-call cost, which matters at scale; (4) **Multilingual support** — not a concern here, but would matter if the corpus included reviews in other languages.

---

## Grounded Generation

**System prompt grounding instruction:**
```
You are a helpful assistant that answers questions about professors at Grambling State University based solely on student reviews.

Rules:
- Answer using ONLY the information in the student reviews provided below.
- Always cite which source document(s) your answer draws from (e.g. "According to rmp_poe_infoscience.txt...").
- If the reviews do not contain enough information to answer the question, respond with exactly: "I don't have enough information in the available reviews to answer that."
- Never use knowledge from outside the provided reviews, even if you know the answer.
```

The retrieved chunks are passed to the model as plain text in the user message, prefixed with `[Source: filename]` labels so the model can cite them. The `temperature` is set to 0.2 to reduce hallucination risk.

**How source attribution is surfaced in the response:**
Source attribution is enforced two ways: (1) the system prompt instructs the model to cite source filenames in its response text, and (2) after generation, the application programmatically extracts and deduplicates the source filenames from the retrieved chunks and displays them in a separate "Retrieved from" panel in the Gradio interface — so attribution is always present even if the model omits it.

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What do students say about Professor Hart-Simmons' workload? | Over 30 tasks in 4 weeks, work due daily, overwhelming | Correctly described 30+ tasks, daily work, overwhelming summer workload. Cited rmp_hart_simmons_math.txt. | Relevant | Accurate |
| 2 | Is Professor McGowan an easy class to pass? | Yes — show up, take notes, get an A | Balanced: noted easy in-person (notes + study guide = A) but flagged hard online section. Both are accurate from reviews. | Relevant | Partially accurate |
| 3 | What do students think of Professor Poe's teaching style? | Great, pushes students, motivating, effective | Described as effective and motivating; cited specific reviews with dates. Minor: pulled one off-target chunk from rmp_clawson_english.txt. | Partially relevant | Accurate |
| 4 | Which English professors at GSU do students recommend? | Mica Gould and James Clawson | Correctly named Clawson and Gould with supporting quotes. Retrieved two off-topic sources (Davis, McGowan) but did not use them in the answer. | Partially relevant | Accurate |
| 5 | What are the main complaints about Professor Hart-Simmons? | Unresponsive, excessive assignments, delayed grading, poor communication | Listed all 8 specific complaints directly from reviews. Fully grounded. | Relevant | Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:** Q2 — "Is Professor McGowan an easy class to pass?"

**What the system returned:** A balanced answer noting that the in-person class is easy (show up, take notes, get an A) but the online section has problems (excessive reading, unclear attendance policy). The answer was partially accurate but missed clearly stating the dominant student opinion — which is that the in-person class is very manageable.

**Root cause (tied to a specific pipeline stage):** This is a retrieval stage issue combined with a small corpus problem. McGowan has only 5 reviews, and one of them is a negative review of his *online* section. With top-k=5 retrieval, that one negative chunk gets included alongside the four positive ones. Because the chunks are short (200 characters), the negative review about the online class occupies the same retrieval weight as the positive in-person reviews. In a larger corpus, the signal-to-noise ratio would favor the majority opinion more clearly.

**What you would change to fix it:** Two options: (1) increase top-k and add a post-retrieval step that counts the sentiment balance before passing context to the LLM; (2) store the course modality (online vs. in-person) as chunk metadata and filter by it when the query implies a specific context.

---

## Spec Reflection

**One way the spec helped you during implementation:**
The chunking strategy section of `planning.md` forced a specific decision about chunk size before any code was written. When it came time to implement `chunk_text()`, there was no guesswork — the 200-character size and 50-character overlap were already reasoned through. This also made it easy to spot the failure mode during testing: when retrieval was pulling off-target results for the Hart-Simmons query, the anticipated challenge about professor name matching (documented in planning.md) immediately explained why, and pointed to the fix (prepending professor names to chunks).

**One way your implementation diverged from the spec, and why:**
The spec used L2 distance for ChromaDB similarity search. During Milestone 4, retrieval distances were all above 1.0 for the Hart-Simmons query — which is hard to interpret with L2. The implementation was updated to use cosine distance instead (`hnsw:space: cosine`), which produces bounded scores in [0, 1] that are easier to evaluate against the project's "below 0.5 = good match" guideline. This change also improved retrieval quality noticeably.

---

## AI Usage

**Instance 1**

- *What I gave the AI:* The Documents section and Chunking Strategy section from `planning.md`, including the file format of the `.txt` source documents and the specified 200-character chunk size with 50-character overlap.
- *What it produced:* A `load_documents()` function that read all `.txt` files from the `documents/` folder, and a `chunk_text()` function using a sliding-window character split.
- *What I changed or overrode:* The initial version chunked the entire file including the header metadata (professor name, URL, rating). This caused chunks like partial URLs (`"ww.ratemyprofessors.com/..."`) to appear in the vector store. I added a header-stripping step that splits on the first `---` delimiter before chunking, so only review text is embedded.

**Instance 2**

- *What I gave the AI:* The Retrieval Approach section from `planning.md`, the architecture diagram, and the grounding requirement (answer only from retrieved context, cite sources, decline if not enough information).
- *What it produced:* `embed.py` with `embed_and_store()` using `all-MiniLM-L6-v2` and ChromaDB, `retrieve.py` with a `retrieve()` function returning top-5 chunks, and `query.py` with an `ask()` function connecting retrieval to Groq with a grounding system prompt.
- *What I changed or overrode:* Two changes: (1) switched ChromaDB from L2 to cosine distance after observing that L2 scores above 1.0 were hard to interpret and retrieval for professor name queries was weak; (2) added professor name prepending to each chunk in `chunk_documents()` after discovering that reviews using only pronouns ("she", "this professor") failed to match name-based queries like "What do students say about Professor Hart-Simmons?"
