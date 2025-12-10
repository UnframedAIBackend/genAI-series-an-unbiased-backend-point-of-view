from io import BytesIO
from pypdf import PdfReader
from .chunk_strategy_service import ChunkStrategyService
from .chunk_strategy import ChunkStrategy
from .strategies.vanilla_chunk_strategy import VanillaChunkStrategy
from .strategies.langchain_chunk_strategy import LangchainChunkStrategy
from .strategies.chonkie_chunk_strategy import ChonkieChunkStrategy
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
        
        self._strategy_map = {
            ChunkStrategy.VANILLA: VanillaChunkStrategy,
            ChunkStrategy.LANGCHAIN: LangchainChunkStrategy,
            ChunkStrategy.CHONKIE: ChonkieChunkStrategy,
        }

    def chunk_text(self, file_id: str) -> list[str]:
        """Extract text from file and chunk it using the configured strategy."""
        file_bytes = self.file_management_service.get_file(file_id)
        
        if not file_bytes:
            raise ValueError(f"File not found: {file_id}")
        
        text = self._extract_text_from_pdf(file_bytes)
        
        return self.chunk_strategy_service.chunk(text)
    
    def chunk_file_with_strategy(self, file_id: str, strategy: str) -> dict:
        """Chunk a file using a specific strategy (overrides config)."""
        # Validate strategy
        if strategy not in [s.value for s in ChunkStrategy]:
            valid_strategies = ", ".join([s.value for s in ChunkStrategy])
            raise ValueError(
                f"Invalid strategy '{strategy}'. Valid options: {valid_strategies}"
            )
        
        # Get file
        file_bytes = self.file_management_service.get_file(file_id)
        if not file_bytes:
            raise ValueError(f"File not found: {file_id}")
        
        # Extract text from PDF
        text = self._extract_text_from_pdf(file_bytes)
        
        # Get strategy class and chunk
        chunk_size = config.get("CHUNK_SIZE")
        strategy_class = self._strategy_map[strategy]
        chunker = strategy_class(chunk_size=chunk_size)
        chunks = chunker.chunk(text)
        
        # Get file metadata
        file_info = self.file_management_service.get_info(file_id)
        
        return {
            "file_id": file_id,
            "filename": file_info.get("original_filename") if file_info else "unknown",
            "strategy": strategy,
            "chunk_size": chunk_size,
            "total_chunks": len(chunks),
            "chunks": chunks
        }
    
    def _extract_text_from_pdf(self, file_bytes: bytes) -> str:
        """Extract text content from PDF bytes."""
        reader = PdfReader(BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text