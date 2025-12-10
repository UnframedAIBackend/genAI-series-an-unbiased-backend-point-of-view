from .i_chunk_strategy import IChunkStrategy


class VanillaChunkStrategy(IChunkStrategy):
    def __init__(self, chunk_size: int = 1000):
        self.chunk_size = chunk_size
    
    def chunk(self, content: str) -> list[str]:
        """Chunk text into fixed-size chunks by character count."""
        chunks = []
        for i in range(0, len(content), self.chunk_size):
            chunk = content[i:i + self.chunk_size]
            chunks.append(chunk)
        return chunks