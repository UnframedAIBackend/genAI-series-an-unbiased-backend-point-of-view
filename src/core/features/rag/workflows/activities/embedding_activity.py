from temporalio import activity

from src.core.configuration.configuration import config
from src.core.container.container import container
from src.core.features.rag.workflows.activities.activity_output import (
    BatchProcessingResult,
    ChunkData,
    ChunkItem,
)
from src.core.features.vector_store.vector_store_entity import VectorEntity


@activity.defn
class EmbeddingActivity:
    def __init__(self):
        self.embedding_service = container.embedding_service()
        self.vector_store_service = container.vector_store_service()

    @activity.defn
    async def process_and_store_embeddings_batched(self, chunk_data: ChunkData) -> BatchProcessingResult:
        """
        Process chunks in batches: generate embeddings and store directly to vector DB.
        Returns only metadata about processing - no large embedding data through Temporal.

        Activities should persist data directly, not pass large payloads through workflow history.
        """
        try:
            embedding_model = config.get("EMBEDDING_MODEL")
            batch_size = config.get("BATCH_SIZE")

            activity.logger.info(
                f"Starting batch processing: {len(chunk_data.chunks)} total chunks, "
                f"batch size: {batch_size}, model: {embedding_model}"
            )

            total_chunks = len(chunk_data.chunks)
            total_vectors = 0

            for batch_num, i in enumerate(range(0, total_chunks, batch_size), start=1):
                batch_chunks = chunk_data.chunks[i : i + batch_size]
                current_batch_size = len(batch_chunks)

                activity.logger.info(
                    f"Processing batch {batch_num}: chunks {i} to {i + current_batch_size - 1} "
                    f"({current_batch_size} chunks)"
                )

                texts = [chunk.content for chunk in batch_chunks]
                embeddings = self.embedding_service.generate(embedding_model, texts)

                activity.heartbeat()

                total_vectors += await self.save_vectors_in_batch(chunk_data, batch_chunks, embeddings, embedding_model)

            return BatchProcessingResult(
                chunks_processed=total_chunks,
                vectors_stored=total_vectors,
                embedding_model=embedding_model,
            )

        except Exception as e:
            import traceback

            activity.logger.error(f"Batch processing failed: {str(e)}\n{traceback.format_exc()}")
            raise e

    async def save_vectors_in_batch(
        self, chunk_data: ChunkData, batch_chunks: list[ChunkItem], embeddings: list[list[float]], embedding_model: str
    ) -> int:
        vectors = []
        for chunk, embedding in zip(batch_chunks, embeddings, strict=True):
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

        await self.vector_store_service.save(vectors)
        return len(vectors)
