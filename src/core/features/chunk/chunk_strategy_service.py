from typing import Type
from src.core.configuration.configuration import config
from .chunk_strategy import ChunkStrategy
from .strategies.i_chunk_strategy import IChunkStrategy
from .strategies.vanilla_chunk_strategy import VanillaChunkStrategy
from .strategies.langchain_chunk_strategy import LangchainChunkStrategy
from .strategies.chonkie_chunk_strategy import ChonkieChunkStrategy


class ChunkStrategyService:
    _strategies: dict[str, Type[IChunkStrategy]] = {
        ChunkStrategy.VANILLA: VanillaChunkStrategy,
        ChunkStrategy.LANGCHAIN: LangchainChunkStrategy,
        ChunkStrategy.CHONKIE: ChonkieChunkStrategy,
    }

    def __init__(self):
        strategy_type = config.get("CHUNK_STRATEGY")
        chunk_size = config.get("CHUNK_SIZE")
        embedding_model = config.get("EMBEDDING_MODEL")
        
        strategy_class = self._strategies.get(strategy_type)
        if not strategy_class:
            valid_strategies = ", ".join([s.value for s in ChunkStrategy])
            raise ValueError(
                f"Unsupported chunk strategy: {strategy_type}. "
                f"Valid options: {valid_strategies}"
            )
        
        # Instantiate with appropriate parameters
        if strategy_type == ChunkStrategy.CHONKIE:
            self.strategy: IChunkStrategy = strategy_class(
                chunk_size=chunk_size, 
                embedding_model=embedding_model
            )
        else:
            self.strategy: IChunkStrategy = strategy_class(chunk_size=chunk_size)

    def chunk(self, content: str) -> list[str]:
        return self.strategy.chunk(content)
