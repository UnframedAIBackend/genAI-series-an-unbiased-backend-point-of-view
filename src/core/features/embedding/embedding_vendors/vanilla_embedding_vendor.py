from typing import Any

from src.core.features.embedding.embedding_models import EMBEDDING_MODEL_MAP, Embedding
from src.core.features.embedding.embedding_vendors.i_embedding_vendor import IEmbeddingVendor


class VanillaEmbeddingVendor(IEmbeddingVendor):

    def __init__(self):
        self.model = None

    def generate(self, chunks: list[str]) -> list[Any]:
        if not self.model:
            self.model = self.create_model(EMBEDDING_MODEL_MAP[Embedding.VANILLA])

        embeddings = self.model.encode(chunks)
        return embeddings.tolist()
