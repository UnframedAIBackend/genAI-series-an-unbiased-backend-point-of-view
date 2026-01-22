import asyncio

from temporalio import activity
from temporalio.client import Client
from temporalio.runtime import PrometheusConfig, Runtime, TelemetryConfig
from temporalio.worker import Worker

from src.core.configuration.configuration import config
from src.core.features.rag.workflows.activities.chunking_activity import ChunkingActivity
from src.core.features.rag.workflows.activities.embedding_activity import EmbeddingActivity
from src.core.features.rag.workflows.activities.status_update_activity import FileStatusActivity
from src.core.features.rag.workflows.file_processing_workflow import FileProcessingWorkflow


async def main():
    """Start the Temporal worker"""

    temporal_host = config.get("TEMPORAL_HOST")
    temporal_namespace = config.get("TEMPORAL_NAMESPACE")
    task_queue = config.get("TEMPORAL_TASK_QUEUE")

    runtime = Runtime(telemetry=TelemetryConfig(metrics=PrometheusConfig(bind_address="0.0.0.0:9090")))

    client = await Client.connect(
        temporal_host,
        namespace=temporal_namespace,
        runtime=runtime,
        # Increase RPC message size limits to 1GB for large embeddings
        rpc_metadata={
            "grpc.max_receive_message_length": str(1024 * 1024 * 1024),  # 1GB
            "grpc.max_send_message_length": str(1024 * 1024 * 1024),  # 1GB
        },
    )

    chunking_activities = ChunkingActivity()
    embedding_activities = EmbeddingActivity()
    status_activities = FileStatusActivity()

    worker = Worker(
        client,
        task_queue=task_queue,
        workflows=[FileProcessingWorkflow],
        activities=[
            chunking_activities.chunk_file,
            embedding_activities.process_and_store_embeddings_batched,
            status_activities.update_file_status,
        ],
        max_concurrent_activities=10,
        max_concurrent_workflow_tasks=10,
    )

    activity.logger.info("Listening for workflow and activity tasks...")

    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
