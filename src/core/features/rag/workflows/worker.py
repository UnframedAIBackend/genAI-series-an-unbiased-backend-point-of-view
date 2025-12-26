import asyncio
import os

from temporalio.client import Client
from temporalio.worker import Worker

from src.core.configuration.configuration import config
from src.core.features.rag.workflows.activities.chunking_activity import chunk_file
from src.core.features.rag.workflows.activities.embedding_activity import generate_embeddings
from src.core.features.rag.workflows.activities.status_update_activity import update_file_status
from src.core.features.rag.workflows.activities.vector_storage_activity import store_vectors
from src.core.features.rag.workflows.file_processing_workflow import FileProcessingWorkflow


async def main():
    """Start the Temporal worker"""

    # Get configuration from environment
    temporal_host = config.get("TEMPORAL_HOST")
    temporal_namespace = os.getenv("TEMPORAL_NAMESPACE", "default")
    task_queue = os.getenv("TEMPORAL_TASK_QUEUE", "file-processing-queue")

    print(f"Connecting to Temporal at {temporal_host}")

    # Connect to Temporal
    client = await Client.connect(temporal_host, namespace=temporal_namespace)

    print(f"Starting worker on task queue: {task_queue}")

    # Create worker
    worker = Worker(
        client,
        task_queue=task_queue,
        workflows=[FileProcessingWorkflow],
        activities=[
            chunk_file,
            generate_embeddings,
            store_vectors,
            update_file_status
        ],
        max_concurrent_activities=10,
        max_concurrent_workflow_tasks=10
    )

    print("Worker started successfully")
    print("Listening for workflow and activity tasks...")

    # Run the worker
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
