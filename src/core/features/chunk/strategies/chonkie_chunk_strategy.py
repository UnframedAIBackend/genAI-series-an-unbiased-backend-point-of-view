from chonkie import SemanticChunker

from .i_chunk_strategy import IChunkStrategy
from src.core.configuration.configuration import config

class ChonkieChunkStrategy(IChunkStrategy):
    def __init__(self, chunk_size: int = 2048):
        self.chunk_size = chunk_size
        self.chunker = SemanticChunker(
            embedding_model=config.get("EMBEDDING_MODEL"),
            threshold=0.8,
            chunk_size=chunk_size,
            skip_window=1
        )
    
    def chunk(self, content: str) -> list[str]:
        """Chunk text using Chonkie's SemanticChunker."""
        chunks = self.chunker.chunk(content)
        return [chunk.text for chunk in chunks]
