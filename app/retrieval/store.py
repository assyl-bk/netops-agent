from functools import lru_cache
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

COLLECTION = "docs"
EMB_MODEL = "BAAI/bge-small-en-v1.5"   # small, fast on CPU, English docs


@lru_cache
def get_model():
    return SentenceTransformer(EMB_MODEL)


@lru_cache
def get_client():
    return QdrantClient(path="data/qdrant")


def embed(texts: list[str]):
    return get_model().encode(texts, batch_size=32, normalize_embeddings=True,
                              show_progress_bar=True)