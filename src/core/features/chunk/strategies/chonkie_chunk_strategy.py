from chonkie import SemanticChunker

from .i_chunk_strategy import IChunkStrategy
from src.core.configuration.configuration import config

class ChonkieChunkStrategy(IChunkStrategy):
    def __init__(self):
        self.chunker = SemanticChunker(
            embedding_model=config.get("EMBEDDING_MODEL_CHUNK"),
            threshold=0.8,
            chunk_size=config.get("CHUNK_SIZE"),
            skip_window=1
        )

    def chunk(self, content: str) -> list[str]:
        """Chunk text using Chonkie's SemanticChunker."""
        import warnings

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=RuntimeWarning, message="invalid value encountered in divide")
            chunks = self.chunker.chunk(content)

        return [chunk.text for chunk in chunks]
