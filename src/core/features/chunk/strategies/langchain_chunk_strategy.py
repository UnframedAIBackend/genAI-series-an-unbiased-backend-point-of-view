from .i_chunk_strategy import IChunkStrategy
from langchain_text_splitters import RecursiveCharacterTextSplitter


class LangchainChunkStrategy(IChunkStrategy):
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            add_start_index=True
        )
    
    def chunk(self, content: str) -> list[str]:
        """Chunk text using LangChain's RecursiveCharacterTextSplitter."""
        chunks = self.text_splitter.split_text(content)
        return chunks
