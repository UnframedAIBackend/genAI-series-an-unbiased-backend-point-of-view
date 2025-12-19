from temporalio import workflow
from datetime import timedelta

with workflow.unsafe.imports_passed_through():
    from src.core.features.rag.workflows.models import FileProcessingInput, FileProcessingResult
    from src.core.features.rag.workflows.activities.file_metadata_activity import store_file_metadata
    from src.core.features.rag.workflows.activities.chunking_activity import chunk_file
    from src.core.features.rag.workflows.activities.embedding_activity import generate_embeddings
    from src.core.features.rag.workflows.activities.vector_storage_activity import store_vectors
    from src.core.features.rag.workflows.activities.status_update_activity import update_file_status


@workflow.defn
class FileProcessingWorkflow:
    """
    Workflow for processing uploaded files through chunking, embedding, and vector storage.
    
    This workflow orchestrates the complete file processing pipeline:
    1. Store file metadata
    2. Chunk the file using configured strategy
    3. Generate embeddings for chunks
    4. Store vectors in database
    5. Update processing status
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
            # Step 1: Store file metadata with workflow tracking
            await workflow.execute_activity(
                store_file_metadata,
                args=[
                    input_data.file_id,
                    input_data.original_filename,
                    input_data.file_path.split('/')[-1],
                    input_data.file_path,
                    0,  # Size will be updated by the activity
                    workflow_id,
                    workflow_run_id
                ],
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=workflow.RetryPolicy(
                    maximum_attempts=3,
                    initial_interval=timedelta(seconds=1),
                    maximum_interval=timedelta(seconds=10)
                )
            )
            
            # Step 2: Chunk the file
            chunks = await workflow.execute_activity(
                chunk_file,
                args=[input_data.file_path, input_data.chunk_strategy],
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=workflow.RetryPolicy(
                    maximum_attempts=3,
                    initial_interval=timedelta(seconds=2),
                    maximum_interval=timedelta(seconds=30)
                )
            )
            
            workflow.logger.info(f"Chunked file into {len(chunks)} chunks")
            
            # Step 3: Generate embeddings
            embeddings = await workflow.execute_activity(
                generate_embeddings,
                args=[chunks, input_data.embedding_model],
                start_to_close_timeout=timedelta(minutes=10),
                retry_policy=workflow.RetryPolicy(
                    maximum_attempts=3,
                    initial_interval=timedelta(seconds=5),
                    maximum_interval=timedelta(minutes=1)
                )
            )
            
            workflow.logger.info(f"Generated {len(embeddings)} embeddings")
            
            # Step 4: Store vectors in database
            stored_count = await workflow.execute_activity(
                store_vectors,
                args=[
                    embeddings,
                    input_data.db_engine,
                    input_data.indexing_strategy,
                    input_data.file_id
                ],
                start_to_close_timeout=timedelta(minutes=10),
                retry_policy=workflow.RetryPolicy(
                    maximum_attempts=3,
                    initial_interval=timedelta(seconds=5),
                    maximum_interval=timedelta(minutes=1)
                )
            )
            
            workflow.logger.info(f"Stored {stored_count} vectors")
            
            # Step 5: Update status to completed
            await workflow.execute_activity(
                update_file_status,
                args=[input_data.file_id, "completed", None],
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=workflow.RetryPolicy(
                    maximum_attempts=5,
                    initial_interval=timedelta(seconds=1),
                    maximum_interval=timedelta(seconds=10)
                )
            )
            
            return FileProcessingResult(
                file_id=input_data.file_id,
                status="completed",
                chunks_count=len(chunks),
                embeddings_count=len(embeddings)
            )
            
        except Exception as e:
            workflow.logger.error(f"Workflow failed: {str(e)}")
            
            # Update status to failed
            try:
                await workflow.execute_activity(
                    update_file_status,
                    args=[input_data.file_id, "failed", str(e)],
                    start_to_close_timeout=timedelta(seconds=30),
                    retry_policy=workflow.RetryPolicy(maximum_attempts=3)
                )
            except Exception as status_error:
                workflow.logger.error(f"Failed to update status: {str(status_error)}")
            
            return FileProcessingResult(
                file_id=input_data.file_id,
                status="failed",
                chunks_count=0,
                embeddings_count=0,
                error_message=str(e)
            )
