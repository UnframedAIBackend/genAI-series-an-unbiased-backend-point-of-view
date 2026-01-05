import os
from typing import Dict, List

from src.core.configuration.configuration import config
from src.core.features.embedding.embedding_models import Embedding
from src.core.features.embedding.embedding_service import EmbeddingService
from src.core.features.llm.llm_service import LlmService
from src.core.features.rag.workflows.activities.activity_output import FileProcessingInput
from src.core.features.rag.workflows.temporal_client import TemporalClientSingleton
from src.core.features.vector_store.vector_store_service import VectorStoreService


class RagService:
    def __init__(
        self,
        vector_store_service: VectorStoreService,
        embedding_service: EmbeddingService,
        llm_service: LlmService,
    ):
        self.vector_store_service = vector_store_service
        self.embedding_service = embedding_service
        self.llm_service = llm_service

    async def start_file_processing(self, file_metadata: dict) -> dict:
        """
        Starts the RAG workflow for a newly uploaded file.
        """

        # Get Temporal client
        temporal_host = config.get("TEMPORAL_HOST")
        temporal_namespace = config.get("TEMPORAL_NAMESPACE")
        client = await TemporalClientSingleton.get_client(temporal_host, temporal_namespace)

        # Prepare workflow input
        workflow_input = FileProcessingInput(
            file_id=file_metadata["id"],
            file_path=file_metadata["path"],
            original_filename=file_metadata["original_filename"],
            chunk_strategy=config.get("CHUNK_STRATEGY"),
            embedding_model=config.get("EMBEDDING_MODEL_CHUNK"),
            db_engine=config.get("DATABASE_ENGINE"),
            indexing_strategy=os.getenv("INDEXING_STRATEGY", "hnsw"),
        )

        # Start workflow
        task_queue = os.getenv("TEMPORAL_TASK_QUEUE", "file-processing-queue")
        workflow_handle = await client.start_workflow(
            "FileProcessingWorkflow", workflow_input, id=f"file-processing-{file_metadata['id']}", task_queue=task_queue
        )

        return {"workflow_id": workflow_handle.id, "workflow_run_id": workflow_handle.result_run_id}

    async def retrieve(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Retrieves relevant documents based on the query.
        """
        embedding_model = config.get("EMBEDDING_MODEL")
        model_enum = Embedding(embedding_model) if isinstance(embedding_model, str) else embedding_model

        query_vectors = self.embedding_service.generate(model_enum, [query])

        if not query_vectors:
            return []

        return await self.vector_store_service.search(query_vectors[0], limit=limit)

    def generate(self, context: List[Dict], query: str) -> str:
        """
        Generates an answer using the LLM and the provided context.
        """
        context_text = "\n\n".join(
            [f"--- Context {i + 1} (Score: {c.get('score', 0):.4f}) ---\n{c['content']}" for i, c in enumerate(context)]
        )

        print("context_text", context_text)

        augmented_prompt = f"""
You are a helpful assistant. Answer the question based ONLY on the following context.
If the answer is not in the context, say that you don't know.

Context:
{context_text}

Question: {query}

Answer:"""

        return self.llm_service.generate(augmented_prompt)
