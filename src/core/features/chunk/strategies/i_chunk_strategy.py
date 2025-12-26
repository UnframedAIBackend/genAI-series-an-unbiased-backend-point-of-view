from abc import ABC, abstractmethod


class IChunkStrategy(ABC):

    @abstractmethod
    def chunk(self, content: str) -> list[str]:
        """Chunk text content into a list of text chunks."""
        pass
