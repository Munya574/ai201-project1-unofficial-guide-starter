from query import ask

questions = [
    "What do students say about Professor Hart-Simmons' workload?",
    "Is Professor McGowan an easy class to pass?",
    "What do students think of Professor Poe's teaching style?",
    "Which English professors at GSU do students recommend?",
    "What are the main complaints students have about Professor Hart-Simmons?",
]

for i, q in enumerate(questions, 1):
    print(f"\n{'='*70}")
    print(f"Q{i}: {q}")
    print('='*70)
    result = ask(q)
    print(result["answer"])
    print(f"\nSources: {result['sources']}")
