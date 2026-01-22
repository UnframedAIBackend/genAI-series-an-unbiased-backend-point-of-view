from typing import Any

from src.core.features.embedding.embedding_models import EMBEDDING_MODEL_MAP, Embedding
from src.core.features.embedding.embedding_vendors.i_embedding_vendor import IEmbeddingVendor


class ColbertEmbeddingVendor(IEmbeddingVendor):
    def __init__(self):
        self.model = None

    def generate(self, chunks: list[str]) -> list[Any]:
        if not self.model:
            from sentence_transformers import SentenceTransformer, models

            from src.core.configuration.configuration import config

            model_id = EMBEDDING_MODEL_MAP[Embedding.COLBERT]
            token = config.get("HF_TOKEN")

            word_embedding_model = models.Transformer(model_id, model_args={"token": token})
            pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension(), pooling_mode="mean")
            self.model = SentenceTransformer(modules=[word_embedding_model, pooling_model])

        embeddings = self.model.encode(chunks)
        return embeddings.tolist()
