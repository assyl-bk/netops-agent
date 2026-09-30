from app.retrieval.store import COLLECTION, get_client, embed


def search(query: str, k: int = 5) -> list[dict]:
    q = embed([query])[0].tolist()
    hits = get_client().query_points(COLLECTION, query=q, limit=k).points
    return [{"source": h.payload["source"], "text": h.payload["text"],
             "score": round(h.score, 3)} for h in hits]