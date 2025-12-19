from io import BytesIO
from pypdf import PdfReader

from .chunk_strategy_service import ChunkStrategyService
from .chunk_strategy import ChunkStrategy
from ..file_management.file_management_service import FileManagementService
from src.core.configuration.configuration import config


class ChunkStrategyController:

    def __init__(
        self,
        chunk_strategy_service: ChunkStrategyService,
        file_management_service: FileManagementService
    ):
        self.chunk_strategy_service = chunk_strategy_service
        self.file_management_service = file_management_service

    def chunk_file_with_strategy(self, file_id: str, strategy: ChunkStrategy) -> dict:
        file_bytes = self.file_management_service.get_file(file_id)
        if not file_bytes:
            raise ValueError(f"File not found: {file_id}")

        text = self.__extract_text_from_pdf(file_bytes)

        chunks = self.chunk_strategy_service.chunk(strategy, text)

        file_info = self.file_management_service.get_info(file_id)

        return {
            "file_id": file_id,
            "filename": file_info.get("original_filename") if file_info else "unknown",
            "strategy": strategy,
            "chunk_size": config.get("CHUNK_SIZE"),
            "total_chunks": len(chunks),
            "chunks": chunks
        }

    def __extract_text_from_pdf(self, file_bytes: bytes) -> str:
        """Extract text content from PDF bytes."""
        reader = PdfReader(BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
