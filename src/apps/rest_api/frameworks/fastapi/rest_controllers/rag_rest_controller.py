from fastapi import APIRouter

from src.core.container.container import container
from src.core.features.rag.rag_controller import RagController


class RagRestController:
    def __init__(self) -> None:
        self.rag_controller: RagController = container.rag_controller()

        self.router = APIRouter(prefix="/rag", tags=["RAG"])
        self._setup_routes()

    def _setup_routes(self) -> None:
        self.router.add_api_route(
            "/query",
            self.rag_query,
            methods=["GET"],
            summary="RAG Query",
        )

    async def rag_query(self, query: str) -> dict:
        return await self.rag_controller.query(query)


rag_rest_controller = RagRestController()
router = rag_rest_controller.router
