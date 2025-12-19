from temporalio import activity
from typing import List
import os
from pathlib import Path

from src.core.features.rag.workflows.models import ChunkData
from src.core.features.chunk.chunk_strategy_service import ChunkStrategyService


@activity.defn
async def chunk_file(file_path: str, chunk_strategy: str) -> List[ChunkData]:
    """
    Chunk a file using the specified strategy.

    Args:
        file_path: Path to the file to chunk
        chunk_strategy: Strategy to use (semantic, recursive, fixed)

    Returns:
        List of chunk data with content and metadata
    """
    # Read file content
    file_content = Path(file_path).read_text(encoding='utf-8')

    # Initialize chunk service with strategy
    chunk_service = ChunkStrategyService(strategy=chunk_strategy)

    # Process chunks
    chunks = chunk_service.chunk_text(file_content)

    # Convert to ChunkData objects
    chunk_data_list = []
    for idx, chunk in enumerate(chunks):
        chunk_data = ChunkData(
            chunk_id=f"{Path(file_path).stem}_{idx}",
            content=chunk.get('text', chunk.get('content', '')),
            metadata={
                'chunk_index': idx,
                'strategy': chunk_strategy,
                'file_path': file_path,
                **chunk.get('metadata', {})
            }
        )
        chunk_data_list.append(chunk_data)

    activity.logger.info(f"Chunked file {file_path} into {len(chunk_data_list)} chunks using {chunk_strategy} strategy")

    return chunk_data_list
