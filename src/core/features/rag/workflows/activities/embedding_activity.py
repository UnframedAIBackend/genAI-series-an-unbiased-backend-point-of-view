from temporalio import activity

from src.core.configuration.configuration import config
from src.core.container.container import container
from src.core.features.rag.workflows.activities.activity_output import ChunkData, EmbeddingData, EmbeddingItem


@activity.defn
async def generate_embeddings(chunk_data: ChunkData) -> EmbeddingData:
    embedding_model = config.get("EMBEDDING_MODEL")
    embedding_service = container.embedding_service()

    texts = [chunk.content for chunk in chunk_data.chunks]

    embeddings = embedding_service.generate(embedding_model, texts)

    embedding_items = []
    for chunk, embedding in zip(chunk_data.chunks, embeddings):
        embedding_items.append(
            EmbeddingItem(
                content=chunk.content,
                embedding=embedding,
                metadata={
                    **chunk.metadata,
                    "embedding_model": embedding_model,
                    "file_id": chunk.metadata.get("file_id"),
                },
            )
        )

    activity.logger.info(f"Generated {len(embeddings)} embeddings using {embedding_model} model")

    return EmbeddingData(embeddings=embedding_items)
