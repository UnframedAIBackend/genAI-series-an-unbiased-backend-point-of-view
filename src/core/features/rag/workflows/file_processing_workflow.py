from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from temporalio.common import RetryPolicy

    from src.core.features.file_management.file_management_vendors.i_management_vendor import FileStatus
    from src.core.features.rag.workflows.activities.activity_output import FileProcessingInput, FileProcessingResult
    from src.core.features.rag.workflows.activities.chunking_activity import ChunkingActivity
    from src.core.features.rag.workflows.activities.embedding_activity import EmbeddingActivity
    from src.core.features.rag.workflows.activities.status_update_activity import FileStatusActivity


@workflow.defn
class FileProcessingWorkflow:
    """
    Workflow for processing uploaded files through chunking, embedding, and vector storage.

    This workflow follows Temporal best practices:
    1. Chunk the file using configured strategy (returns metadata + chunks)
    2. Process embeddings in batches and store directly to DB (returns only metadata)
    3. Update processing status

    Large data (embeddings) never passes through workflow history - stored directly by activities.
    """

    @workflow.run
    async def run(self, input_data: FileProcessingInput) -> FileProcessingResult:
        """
        Execute the file processing workflow.

        Args:
            input_data: File processing configuration and metadata

        Returns:
            FileProcessingResult with processing statistics
        """

        try:
            # Step 1: Chunk the file
            chunk_data = await workflow.execute_activity(
                ChunkingActivity.chunk_file,
                args=[input_data],
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=RetryPolicy(
                    maximum_attempts=3, initial_interval=timedelta(seconds=2), maximum_interval=timedelta(seconds=30)
                ),
            )

            workflow.logger.info(f"Chunked file into {len(chunk_data.chunks)} chunks")

            batch_result = await workflow.execute_activity(
                EmbeddingActivity.process_and_store_embeddings_batched,
                args=[chunk_data],
                start_to_close_timeout=timedelta(minutes=30),
                heartbeat_timeout=timedelta(seconds=30),
                retry_policy=RetryPolicy(
                    maximum_attempts=3, initial_interval=timedelta(seconds=5), maximum_interval=timedelta(minutes=1)
                ),
            )

            workflow.logger.info(
                f"Processed {batch_result.vectors_stored} embeddings", extra={"batch_result": batch_result}
            )

            await workflow.execute_activity(
                FileStatusActivity.update_file_status,
                args=[input_data.file_id, FileStatus.COMPLETED.value, None],
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=RetryPolicy(
                    maximum_attempts=5, initial_interval=timedelta(seconds=1), maximum_interval=timedelta(seconds=10)
                ),
            )

            return FileProcessingResult(
                file_id=input_data.file_id,
                status=FileStatus.COMPLETED.value,
                chunks_count=len(chunk_data.chunks),
                embeddings_count=batch_result.vectors_stored,
            )

        except Exception as e:
            import traceback

            workflow.logger.error(f"Workflow failed: {str(e)}")
            workflow.logger.error(f"Exception type: {type(e).__name__}")
            workflow.logger.error(f"Traceback: {traceback.format_exc()}")

            try:
                await workflow.execute_activity(
                    FileStatusActivity.update_file_status,
                    args=[input_data.file_id, FileStatus.FAILED.value, str(e)],
                    start_to_close_timeout=timedelta(seconds=30),
                    retry_policy=RetryPolicy(maximum_attempts=3),
                )
            except Exception as status_error:
                workflow.logger.error(f"Failed to update status: {str(status_error)}")

            return FileProcessingResult(
                file_id=input_data.file_id,
                status=FileStatus.FAILED.value,
                chunks_count=0,
                embeddings_count=0,
                error_message=str(e),
            )
