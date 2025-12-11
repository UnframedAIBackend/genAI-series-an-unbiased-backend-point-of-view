from fastapi import APIRouter, HTTPException, Path
from src.core.container.container import container
from src.core.features.chunk.chunk_strategy_controller import ChunkStrategyController
from src.core.features.chunk.chunk_strategy import ChunkStrategy


class ChunkStrategyRestController:
    def __init__(self) -> None:
        self.chunk_strategy_controller: ChunkStrategyController = container.chunk_strategy_controller()
        
        self.router = APIRouter(prefix="/chunk", tags=["chunking"])
        self._setup_routes()

    def _setup_routes(self) -> None:
        self.router.add_api_route(
            "/{strategy}/file/{file_id}",
            self.chunk_file,
            methods=["GET"],
            summary="Chunk file using specified strategy",
        )

    async def chunk_file(
        self,
        strategy: ChunkStrategy = Path(..., description="Chunking strategy"),
        file_id: str = Path(..., description="File ID")
    ) -> dict:
        """Chunk a file using the specified strategy."""
        try:
            return self.chunk_strategy_controller.chunk_file_with_strategy(file_id, strategy.value)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Chunking failed: {str(e)}")


chunk_strategy_rest_controller = ChunkStrategyRestController()
router = chunk_strategy_rest_controller.router
