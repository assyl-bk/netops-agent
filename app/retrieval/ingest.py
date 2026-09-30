from qdrant_client.models import Distance, VectorParams, PointStruct
from app.retrieval.chunking import read_docs, chunk_text
from app.retrieval.store import COLLECTION, get_client, get_model, embed


def ingest():
    client = get_client()
    if client.collection_exists(COLLECTION):
        client.delete_collection(COLLECTION)
    client.create_collection(
        COLLECTION,
        vectors_config=VectorParams(
            size=get_model().get_sentence_embedding_dimension(),
            distance=Distance.COSINE),
    )

    texts, payloads = [], []
    for path, text in read_docs():
        for i, ch in enumerate(chunk_text(text)):
            texts.append(ch)
            payloads.append({"source": f"{path.name}#c{i:03d}",
                             "file": path.as_posix(), "text": ch})
    print(f"{len(texts)} chunks to embed")

    vecs = embed(texts)
    points = [PointStruct(id=i, vector=v.tolist(), payload=payloads[i])
              for i, v in enumerate(vecs)]
    for s in range(0, len(points), 256):
        client.upsert(collection_name=COLLECTION, points=points[s:s + 256])
    print("done:", len(points), "points stored")


if __name__ == "__main__":
    ingest()