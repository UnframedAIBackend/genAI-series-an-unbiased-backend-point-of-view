from temporalio import activity

from src.core.container.container import container
from src.core.features.rag.workflows.activities.activity_output import ChunkData
from src.core.configuration.configuration import config


@activity.defn
async def chunk_file(file_id: str) -> ChunkData:
    file_management_service = container.file_management_service()
    chunk_strategy_service = container.chunk_strategy_service()
    
    file_content_bytes = file_management_service.get_file(file_id)
    if not file_content_bytes:
        raise ValueError(f"Could not retrieve content for file {file_id}")
    
    file_content = file_content_bytes.decode('utf-8')
    
    strategy = config.get("CHUNK_STRATEGY")
    
    chunks_text = chunk_strategy_service.chunk(strategy, file_content)
    
    chunk_items = []
    for idx, text in enumerate(chunks_text):
        chunk_items.append(ChunkItem(
            content=text,
            metadata={
                "file_id": file_id,
                "chunk_index": idx,
                "total_chunks": len(chunks_text)
            }
        ))
    
    activity.logger.info(
        f"Chunked file {file_id} "
        f"into {len(chunk_items)} chunks using {strategy} strategy"
    )
    
    return ChunkData(strategy=strategy, chunks=chunk_items)
