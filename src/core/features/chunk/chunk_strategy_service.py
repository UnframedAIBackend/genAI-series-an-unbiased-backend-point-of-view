from pathlib import Path
from typing import Type

from pypdf import PdfReader

from src.core.configuration.configuration import config
from .chunk_strategy import ChunkStrategy
from .strategies.chonkie_chunk_strategy import ChonkieChunkStrategy
from .strategies.i_chunk_strategy import IChunkStrategy
from .strategies.langchain_chunk_strategy import LangchainChunkStrategy
from .strategies.vanilla_chunk_strategy import VanillaChunkStrategy


class ChunkStrategyService:
    __strategies: dict[str, Type[IChunkStrategy]] = {
        ChunkStrategy.VANILLA: VanillaChunkStrategy(),
        ChunkStrategy.LANGCHAIN: LangchainChunkStrategy(),
        ChunkStrategy.CHONKIE: ChonkieChunkStrategy(),
    }

    def get_file_content(self, path: str, file_type: str = "pdf") -> str:
        file_path = Path(path)
        if not file_path.is_absolute():
            uploads_path = config.get("UPLOADS_PATH")
            file_path = Path(uploads_path) / file_path

        if file_type == "pdf":
            return self.__extract_text_from_pdf(str(file_path))
        else:
            raise ValueError(f"File type '{file_type}' not supported")

    def __extract_text_from_pdf(self, path: str) -> str:
        reader = PdfReader(path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text

    def chunk(self, strategy_type: ChunkStrategy, content: str) -> list[str]:
        strategy_class = self.__get_strategy_class(strategy_type)
        return strategy_class.chunk(content)

    def __get_strategy_class(self, strategy_type: ChunkStrategy) -> Type[IChunkStrategy]:
        strategy_class = self.__strategies.get(strategy_type)
        if not strategy_class:
            valid_strategies = ", ".join([s.value for s in ChunkStrategy])
            raise ValueError(f"Unsupported chunk strategy: {strategy_type}. Valid options: {valid_strategies}")
        return strategy_class
