import asyncio
import logging as std_logging

from temporalio.client import Client
from temporalio.worker import Worker
from temporalio.runtime import Runtime, TelemetryConfig, PrometheusConfig

from src.core.configuration.configuration import config
from src.core.features.rag.workflows.activities.chunking_activity import chunk_file
from src.core.features.rag.workflows.activities.embedding_activity import process_and_store_embeddings_batched
from src.core.features.rag.workflows.activities.status_update_activity import update_file_status
from src.core.features.rag.workflows.file_processing_workflow import FileProcessingWorkflow


async def main():
    """Start the Temporal worker"""

    # Configure logging to output to stdout - use DEBUG to see serialization errors
    std_logging.basicConfig(level=std_logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    temporal_host = config.get("TEMPORAL_HOST")
    temporal_namespace = config.get("TEMPORAL_NAMESPACE")
    task_queue = config.get("TEMPORAL_TASK_QUEUE")

    print(f"Connecting to Temporal at {temporal_host}")

    # Configure runtime with increased payload size limits
    runtime = Runtime(
        telemetry=TelemetryConfig(
            metrics=PrometheusConfig(bind_address="0.0.0.0:9090")
        )
    )

    client = await Client.connect(
        temporal_host, 
        namespace=temporal_namespace,
        runtime=runtime,
        # Increase RPC message size limits to 1GB for large embeddings
        rpc_metadata={
            "grpc.max_receive_message_length": str(1024 * 1024 * 1024),  # 1GB
            "grpc.max_send_message_length": str(1024 * 1024 * 1024),     # 1GB
        }
    )

    worker = Worker(
        client,
        task_queue=task_queue,
        workflows=[FileProcessingWorkflow],
        activities=[
            chunk_file, 
            process_and_store_embeddings_batched,  # Combined activity: generate + store in batches
            update_file_status
        ],
        max_concurrent_activities=10,
        max_concurrent_workflow_tasks=10,
    )

    print("Listening for workflow and activity tasks...")

    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
