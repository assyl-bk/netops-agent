from app.retrieval.search import search

for q in ["How does BGP withdraw a route?",
          "What does the MME do in the core network?",
          "How is a DNS query resolved?"]:
    print("\n", q)
    for h in search(q, 3):
        print(f"  {h['score']}  {h['source']}  |  {h['text'][:110]!r}")