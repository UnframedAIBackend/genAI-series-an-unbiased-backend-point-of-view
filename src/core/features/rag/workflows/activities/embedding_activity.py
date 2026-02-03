from temporalio import activity

from src.core.configuration.configuration import config
from src.core.container.container import container
from src.core.features.rag.workflows.activities.activity_output import (
    ChunkData,
    BatchProcessingResult,
)
from src.core.features.vector_store.vector_store_entity import VectorEntity

# Batch size for processing embeddings
BATCH_SIZE = 50  # Process 50 chunks at a time to avoid memory/payload issues


@activity.defn
async def process_and_store_embeddings_batched(chunk_data: ChunkData) -> list[BatchProcessingResult]:
    """
    Process chunks in batches: generate embeddings and store directly to vector DB.
    Returns only metadata about processing - no large embedding data through Temporal.
    
    Best practice: Activities should persist data directly, not pass large payloads through workflow history.
    """
    try:
        embedding_model = config.get("EMBEDDING_MODEL")
        embedding_service = container.embedding_service()
        vector_store_service = container.vector_store_service()
        
        activity.logger.info(
            f"Starting batch processing: {len(chunk_data.chunks)} total chunks, "
            f"batch size: {BATCH_SIZE}, model: {embedding_model}"
        )
        
        batch_results = []
        total_chunks = len(chunk_data.chunks)
        
        # Process in batches
        for batch_num, i in enumerate(range(0, total_chunks, BATCH_SIZE), start=1):
            batch_chunks = chunk_data.chunks[i:i + BATCH_SIZE]
            batch_size = len(batch_chunks)
            
            activity.logger.info(
                f"Processing batch {batch_num}: chunks {i} to {i + batch_size - 1} "
                f"({batch_size} chunks)"
            )
            
            # Generate embeddings for this batch
            texts = [chunk.content for chunk in batch_chunks]
            embeddings = embedding_service.generate(embedding_model, texts)
            
            activity.logger.info(f"Generated {len(embeddings)} embeddings for batch {batch_num}")
            
            # Prepare vectors for storage
            vectors = []
            for chunk, embedding in zip(batch_chunks, embeddings):
                vectors.append(
                    VectorEntity(
                        file_id=chunk_data.file_id,
                        content=chunk.content,
                        embedding=embedding,
                        metadata={
                            **chunk.metadata,
                            "embedding_model": embedding_model,
                            "file_id": chunk_data.file_id,
                        },
                    )
                )
            
            # Store directly to vector database
            await vector_store_service.save(vectors)
            
            activity.logger.info(f"Stored {len(vectors)} vectors for batch {batch_num}")
            
            # Return only metadata (small payload)
            batch_results.append(
                BatchProcessingResult(
                    batch_number=batch_num,
                    chunks_processed=batch_size,
                    vectors_stored=len(vectors),
                    embedding_model=embedding_model,
                )
            )
            
            # Heartbeat to show progress for long-running activity
            activity.heartbeat(f"Processed batch {batch_num}/{(total_chunks + BATCH_SIZE - 1) // BATCH_SIZE}")
        
        activity.logger.info(
            f"Completed all batches: {len(batch_results)} batches, "
            f"{sum(r.vectors_stored for r in batch_results)} total vectors stored"
        )
        
        return batch_results
        
    except Exception as e:
        import traceback
        activity.logger.error(f"Batch processing failed: {str(e)}\n{traceback.format_exc()}")
        raise e
