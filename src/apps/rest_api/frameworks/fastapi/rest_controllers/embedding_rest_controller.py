from typing import Any

from fastapi import APIRouter, Path
from pydantic import BaseModel

from src.core.container.container import container
from src.core.features.embedding.embedding_controller import EmbeddingController
from src.core.features.embedding.embedding_models import Embedding


class EmbeddingRequest(BaseModel):
    chunks: list[str]

class EmbeddingResponse(BaseModel):
    model_id: Embedding
    total_chunks: int
    embeddings: list[Any]


class EmbeddingRestController:
    def __init__(self):
        self.embedding_controller: EmbeddingController = container.embedding_controller()
        self.router = APIRouter(prefix="/embedding", tags=["embedding"])
        self._setup_routes()

    def _setup_routes(self):
        self.router.add_api_route(
            "/{model_id}/generate",
            self.generate_embeddings,
            methods=["POST"],
            response_model=EmbeddingResponse
        )

    async def generate_embeddings(
        self,
        request: EmbeddingRequest,
        model_id: Embedding = Path(..., description="Embedding model to use")
    ) -> EmbeddingResponse:
        result = self.embedding_controller.generate_embeddings(model_id, request.chunks)
        return EmbeddingResponse(**result)


embedding_rest_controller = EmbeddingRestController()
router = embedding_rest_controller.router
