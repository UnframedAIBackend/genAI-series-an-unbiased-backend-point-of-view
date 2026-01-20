import asyncio
import logging
import os
import time
from typing import Any, Dict

try:
    import mlflow
except ImportError:
    print("MLflow not found, proceeding without it.")
    mlflow = None
except Exception as e:
    print(f"Error importing MLflow: {e}, proceeding without it.")
    mlflow = None

from datasets import Dataset
from dotenv import find_dotenv, load_dotenv
from langchain_ollama import ChatOllama, OllamaEmbeddings
from ragas import evaluate
from ragas.metrics import (
    answer_relevancy,
    context_precision,
    context_recall,
    faithfulness,
)

# Corrected Ragas Imports for v0.2+
try:
    from ragas.testset import TestsetGenerator
except ImportError:
    # Fallback/Debug
    from ragas.testset.synthesizers.generate import TestsetGenerator

from src.core.configuration.configuration import config
from src.core.features.rag.rag_controller import RagController
from src.core.features.rag.rag_service import RagService
from src.core.features.vector_store.vector_store_service import VectorStoreService
from src.core.features.embedding.embedding_service import EmbeddingService
from src.core.features.llm.llm_service import LlmService
from src.core.features.vector_store.vector_store_repository import VectorStoreRepository
from src.core.features.embedding.embedding_models import Embedding

# Configure logging to ensure stdout capture
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

load_dotenv(find_dotenv())

# Configuration constants
OLLAMA_BASE_URL = os.getenv("OLLAMA_HOST", "http://localhost:11434")
PDF_PATH = os.path.abspath("test/assets/pdf/Y2Ksurveyreport.pdf")
EVAL_EXPERIMENT_NAME = "Ragas_RAG_Benchmark"

# Define the matrix of configurations to test
CHUNKING_STRATEGIES = ["recursive"]
EMBEDDING_MODELS = ["nomic-embed-text"]


class RAGEvaluationPipeline:
    def __init__(self):
        self.llm = ChatOllama(model="tinyllama", base_url=OLLAMA_BASE_URL, temperature=0)
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url=OLLAMA_BASE_URL)

    async def setup_rag_service(self, chunk_strategy: str, embedding_model: str) -> RagService:
        vector_repo = VectorStoreRepository()
        vector_store_service = VectorStoreService(vector_repo)
        embedding_service = EmbeddingService()
        llm_service = LlmService()

        return RagService(
            vector_store_service=vector_store_service, embedding_service=embedding_service, llm_service=llm_service
        )

    async def ingest_document(self, rag_service: RagService, file_metadata: Dict[str, Any]):
        logger.info(f"Starting ingestion for {file_metadata['original_filename']}")
        if not os.getenv("TEMPORAL_HOST"):
            logger.warning("TEMPORAL_HOST not set, ingestion might fail if not using defaults.")

        result = await rag_service.start_file_processing(file_metadata)
        workflow_id = result["workflow_id"]
        logger.info(f"Workflow started: {workflow_id}. Waiting for completion...")

        time.sleep(10)
        logger.info("Ingestion wait complete.")

    def generate_testset(self, document_path: str, test_size: int = 5) -> Dataset:
        logger.info("Generating testset...")
        from langchain_community.document_loaders import PyPDFLoader

        loader = PyPDFLoader(document_path)
        documents = loader.load()

        generator = TestsetGenerator.from_langchain(
            generator_llm=self.llm,
            critic_llm=self.llm,
            embeddings=self.embeddings,
        )

        # Use defaults for distributions which handles 0.2+ logic
        testset = generator.generate_with_langchain_docs(documents, test_size=test_size)
        return testset.to_dataset()

    async def evaluate_config(self, chunk_strategy: str, embedding_model: str, testset: Dataset):
        logger.info(f"Evaluating Config: Chunk={chunk_strategy}, Embed={embedding_model}")

        os.environ["CHUNK_STRATEGY"] = chunk_strategy
        os.environ["EMBEDDING_MODEL_CHUNK"] = embedding_model

        rag_service = await self.setup_rag_service(chunk_strategy, embedding_model)
        rag_controller = RagController(rag_service)

        file_id = f"test_{int(time.time())}"
        file_metadata = {"id": file_id, "path": PDF_PATH, "original_filename": "Y2Ksurveyreport.pdf"}
        await self.ingest_document(rag_service, file_metadata)

        questions = testset["question"]
        ground_truths = testset["ground_truth"]

        answers = []
        contexts = []

        for q in questions:
            result = await rag_controller.query(q)
            answers.append(result["answer"])
            retrieved_contexts = [doc.get("content", "") for doc in result.get("retrieved_docs", [])]
            contexts.append(retrieved_contexts)

        eval_data = {"question": questions, "answer": answers, "contexts": contexts, "ground_truth": ground_truths}
        eval_dataset = Dataset.from_dict(eval_data)

        results = evaluate(
            dataset=eval_dataset,
            metrics=[
                context_precision,
                context_recall,
                faithfulness,
                answer_relevancy,
            ],
            llm=self.llm,
            embeddings=self.embeddings,
        )

        logger.info(f"Evaluation Results for {chunk_strategy}/{embedding_model}: {results}")

        if mlflow:
            try:
                with mlflow.start_run(run_name=f"{chunk_strategy}_{embedding_model}"):
                    mlflow.log_params({"chunk_strategy": chunk_strategy, "embedding_model": embedding_model})
                    mlflow.log_metrics(results)

                    df = results.to_pandas()
                    mlflow.log_table(df, "eval_results.json")
            except Exception as e:
                logger.warning(f"Failed to log to MLflow: {e}")

    async def run(self):
        if mlflow:
            try:
                mlflow.set_tracking_uri("http://localhost:5000")
                mlflow.set_experiment(EVAL_EXPERIMENT_NAME)
                logger.info("Connected to MLflow")
            except Exception as e:
                logger.warning(f"MLflow setup failed: {e}")
        else:
            logger.info("Running without MLflow")

        try:
            testset = self.generate_testset(PDF_PATH, test_size=2)
            logger.info(f"Testset generated with {len(testset)} items")
        except Exception as e:
            logger.error(f"Testset generation failed: {e}")
            return

        for chunk_strategy in CHUNKING_STRATEGIES:
            for embedding_model in EMBEDDING_MODELS:
                try:
                    await self.evaluate_config(chunk_strategy, embedding_model, testset)
                except Exception as e:
                    logger.error(f"Failed to run eval for {chunk_strategy}/{embedding_model}: {e}")


if __name__ == "__main__":
    pipeline = RAGEvaluationPipeline()
    asyncio.run(pipeline.run())
