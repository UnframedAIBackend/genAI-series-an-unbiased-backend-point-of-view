from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from temporalio.common import RetryPolicy

    from src.core.features.file_management.file_management_vendors.i_management_vendor import FileStatus
    from src.core.features.rag.workflows.activities.activity_output import FileProcessingInput, FileProcessingResult
    from src.core.features.rag.workflows.activities.chunking_activity import chunk_file
    from src.core.features.rag.workflows.activities.embedding_activity import generate_embeddings
    from src.core.features.rag.workflows.activities.status_update_activity import update_file_status
    from src.core.features.rag.workflows.activities.vector_storage_activity import store_vectors


@workflow.defn
class FileProcessingWorkflow:
    """
    Workflow for processing uploaded files through chunking, embedding, and vector storage.

    This workflow orchestrates the complete file processing pipeline:
    1. Chunk the file using configured strategy
    2. Generate embeddings for chunks
    3. Store vectors in database
    4. Update processing status
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
        workflow_id = workflow.info().workflow_id
        workflow_run_id = workflow.info().run_id

        try:
            chunk_data = await workflow.execute_activity(
                chunk_file,
                args=[input_data],
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=RetryPolicy(
                    maximum_attempts=3, initial_interval=timedelta(seconds=2), maximum_interval=timedelta(seconds=30)
                ),
            )

            workflow.logger.info(f"Chunked file into {len(chunk_data.chunks)} chunks")

            embedding_data = await workflow.execute_activity(
                generate_embeddings,
                args=[chunk_data],
                start_to_close_timeout=timedelta(minutes=10),
                retry_policy=RetryPolicy(
                    maximum_attempts=3, initial_interval=timedelta(seconds=5), maximum_interval=timedelta(minutes=1)
                ),
            )

            workflow.logger.info(f"Generated {len(embedding_data.embeddings)} embeddings")

            stored_count = await workflow.execute_activity(
                store_vectors,
                args=[
                    embedding_data,
                ],
                start_to_close_timeout=timedelta(minutes=10),
                retry_policy=RetryPolicy(
                    maximum_attempts=3, initial_interval=timedelta(seconds=5), maximum_interval=timedelta(minutes=1)
                ),
            )

            workflow.logger.info(f"Stored {stored_count} vectors")

            # Step 5: Update status to completed
            await workflow.execute_activity(
                update_file_status,
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
                embeddings_count=len(embedding_data.embeddings),
            )

        except Exception as e:
            workflow.logger.error(f"Workflow failed: {str(e)}")

            try:
                await workflow.execute_activity(
                    update_file_status,
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
