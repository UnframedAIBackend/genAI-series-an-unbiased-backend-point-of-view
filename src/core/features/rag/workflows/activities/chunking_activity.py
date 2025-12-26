from temporalio import activity

from src.core.configuration.configuration import config
from src.core.container.container import container
from src.core.features.rag.workflows.activities.activity_output import (
    ChunkData,
    ChunkItem,
    FileProcessingInput,
)


@activity.defn
async def chunk_file(input_data: FileProcessingInput) -> ChunkData:
    chunk_strategy_service = container.chunk_strategy_service()

    file_type = "pdf" if input_data.file_path.lower().endswith(".pdf") else "text"
    file_content = chunk_strategy_service.get_file_content(input_data.file_path, file_type)
    print(
        "filecontent: ",
        input_data.file_id,
        input_data.file_path,
        "bytes length:",
        file_content[:10],
    )
    if not file_content:
        raise ValueError(f"Could not retrieve content for file {input_data.file_id} at {input_data.file_path}")

    strategy = config.get("CHUNK_STRATEGY")

    chunks_text = chunk_strategy_service.chunk(strategy, file_content)

    chunk_items = []
    for idx, text in enumerate(chunks_text):
        chunk_items.append(
            ChunkItem(
                content=text,
                metadata={"file_id": input_data.file_id, "chunk_index": idx, "total_chunks": len(chunks_text)},
            )
        )

    activity.logger.info(f"Chunked file {input_data.file_id} into {len(chunk_items)} chunks using {strategy} strategy")

    return ChunkData(strategy=strategy, chunks=chunk_items)
