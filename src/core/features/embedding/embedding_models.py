from enum import StrEnum


class Embedding(StrEnum):
    VANILLA = "vanilla"
    GEMMA = "gemma"
    COLBERT = "colbert"


EMBEDDING_MODEL_MAP = {
    Embedding.VANILLA: "all-MiniLM-L6-v2",
    Embedding.GEMMA: "google/embeddinggemma-300m",
    Embedding.COLBERT: "colbert-ir/colbertv2.0"
}
