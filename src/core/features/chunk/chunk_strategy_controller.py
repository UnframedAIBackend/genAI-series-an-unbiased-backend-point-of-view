from src.core.configuration.configuration import config

from ..file_management.file_management_service import FileManagementService
from .chunk_strategy import ChunkStrategy
from .chunk_strategy_service import ChunkStrategyService


class ChunkStrategyController:
    def __init__(self, chunk_strategy_service: ChunkStrategyService, file_management_service: FileManagementService):
        self.chunk_strategy_service = chunk_strategy_service
        self.file_management_service = file_management_service

    def chunk_file_with_strategy(self, file_id: str, strategy: ChunkStrategy) -> dict:
        file_info = self.file_management_service.get_info(file_id)
        if not file_info:
            raise ValueError(f"File not found: {file_id}")

        if isinstance(file_info, dict):
            path = file_info.get("path")
            filename = file_info.get("original_filename", "")
        else:
            path = getattr(file_info, "path", None)
            filename = getattr(file_info, "original_filename", "")

        if not path:
            raise ValueError(f"File path not found in metadata for file: {file_id}")

        file_type = "pdf" if filename.lower().endswith(".pdf") else "text"
        text = self.chunk_strategy_service.get_file_content(path, file_type)

        chunks = self.chunk_strategy_service.chunk(strategy, text)

        return {
            "file_id": file_id,
            "filename": filename,
            "strategy": strategy,
            "chunk_size": config.get("CHUNK_SIZE"),
            "total_chunks": len(chunks),
            "chunks": chunks,
        }
