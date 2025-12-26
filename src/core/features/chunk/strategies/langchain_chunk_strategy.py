from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.core.configuration.configuration import config

from .i_chunk_strategy import IChunkStrategy


class LangchainChunkStrategy(IChunkStrategy):
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.get("CHUNK_SIZE"),
            chunk_overlap=config.get("CHUNK_OVERLAP"),
            add_start_index=True
        )

    def chunk(self, content: str) -> list[str]:
        """Chunk text using LangChain's RecursiveCharacterTextSplitter."""
        chunks = self.text_splitter.split_text(content)
        return chunks
