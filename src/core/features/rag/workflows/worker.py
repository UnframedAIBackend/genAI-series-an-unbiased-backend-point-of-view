import asyncio
import logging as std_logging

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

    # Configure logging to output to stdout
    std_logging.basicConfig(level=std_logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    temporal_host = config.get("TEMPORAL_HOST")
    temporal_namespace = config.get("TEMPORAL_NAMESPACE")
    task_queue = config.get("TEMPORAL_TASK_QUEUE")

    print(f"Connecting to Temporal at {temporal_host}")

    client = await Client.connect(temporal_host, namespace=temporal_namespace)

    worker = Worker(
        client,
        task_queue=task_queue,
        workflows=[FileProcessingWorkflow],
        activities=[chunk_file, generate_embeddings, store_vectors, update_file_status],
        max_concurrent_activities=10,
        max_concurrent_workflow_tasks=10,
    )

    print("Listening for workflow and activity tasks...")

    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
