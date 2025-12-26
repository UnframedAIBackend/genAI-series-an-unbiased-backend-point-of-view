from .embedding_models import Embedding
from .embedding_service import EmbeddingService


class EmbeddingController:

    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service

    def generate_embeddings(self, model_id: Embedding, chunks: list[str]) -> dict:
        embeddings = self.embedding_service.generate(model_id, chunks)

        # For demonstration purposes, we limit the output to 10 vectors
        # to avoid massive payloads in the response.
        return {
            "model_id": model_id,
            "total_chunks": len(chunks),
            "embeddings": embeddings[:10]
        }
