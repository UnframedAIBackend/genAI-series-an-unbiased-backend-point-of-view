from typing import Type
from src.core.configuration.configuration import config
from .chunk_strategy import ChunkStrategy
from .strategies.i_chunk_strategy import IChunkStrategy
from .strategies.vanilla_chunk_strategy import VanillaChunkStrategy
from .strategies.langchain_chunk_strategy import LangchainChunkStrategy
from .strategies.chonkie_chunk_strategy import ChonkieChunkStrategy

class ChunkStrategyService:
    __strategies: dict[str, Type[IChunkStrategy]] = {
        ChunkStrategy.VANILLA: VanillaChunkStrategy(),
        ChunkStrategy.LANGCHAIN: LangchainChunkStrategy(),
        ChunkStrategy.CHONKIE: ChonkieChunkStrategy(),
    }        

    def chunk(self, strategy_type: ChunkStrategy, content: str) -> list[str]:
        strategy_class = self.__get_strategy_class(strategy_type)
        return strategy_class.chunk(content)

    def __get_strategy_class(self, strategy_type: ChunkStrategy) -> Type[IChunkStrategy]:
        strategy_class = self.__strategies.get(strategy_type)
        if not strategy_class:
            valid_strategies = ", ".join([s.value for s in ChunkStrategy])
            raise ValueError(
                f"Unsupported chunk strategy: {strategy_type}. "
                f"Valid options: {valid_strategies}"
            )
        return strategy_class
