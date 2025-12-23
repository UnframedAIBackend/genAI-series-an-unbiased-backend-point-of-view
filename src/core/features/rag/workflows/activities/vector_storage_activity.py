from temporalio import activity
from typing import List

from src.core.container.container import container
from src.core.features.rag.workflows.activities.activity_output import EmbeddingData
from src.core.features.vector_store.vector_store_entity import VectorEntity

@activity.defn
async def store_vectors(
    embedding_data: EmbeddingData
) -> int:
    
    vector_store_service = container.vector_store_service()
    
    vectors = [
        VectorEntity(
             file_id=item.file_id,
             content=item.content,
             embedding=item.embedding,
             metadata=item.metadata
        )
        for item in embedding_data.embeddings
    ]
    
    await vector_store_service.save(vectors)

    count = len(vectors)
    activity.logger.info(f"Stored {count} vectors")
    return count
