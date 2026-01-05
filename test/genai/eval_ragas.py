import mlflow
from datasets import Dataset
from langchain_ollama import ChatOllama, OllamaEmbeddings
from ragas import evaluate
from ragas.metrics import (
    answer_relevancy,
    context_precision,
    context_recall,
    faithfulness,
)

# Configuration for Local LLM (Self-contained)
# Connection to local Ollama instance running in Docker
OLLAMA_BASE_URL = "http://localhost:11434"

# Initialize LLM & Embeddings
# Ragas uses these to judge the quality of the RAG pipeline.
llm = ChatOllama(model="tinyllama", base_url=OLLAMA_BASE_URL, temperature=0)

embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url=OLLAMA_BASE_URL)

# Example Data for Evaluation (Golden Dataset)
# In production, this data comes from logging actual user queries and retrieving the system's response + context.
data = {
    "question": [
        "What is the advantage of vector databases?",
        "How is HNSW different from IVF?",
    ],
    "answer": [
        "Vector databases enable semantic search by interacting with embeddings rather than keywords.",
        "HNSW uses a graph-based approach for static data, while IVF uses inverted files for faster search in dynamic datasets.",
    ],
    "contexts": [
        [
            "Vector databases store high-dimensional vectors for semantic search.",
            "They help finding similar items based on meaning.",
        ],
        ["HNSW is a graph-based indexing algorithm.", "IVF (Inverted File Index) clusters vectors to speed up search."],
    ],
    "ground_truth": [
        "Vector databases allow for semantic search using high-dimensional vectors.",
        "HNSW is graph-based, IVF is cluster-based.",
    ],
}


def run_evaluation():
    try:
        # Check if MLflow is reachable
        mlflow.set_tracking_uri("http://localhost:5000")
        mlflow.set_experiment("Ragas_Local_Eval")
        print("Connected to MLflow at http://localhost:5000")
    except Exception as e:
        print(f"Warning: MLflow connection failed ({e}). Running without logging to MLflow server.")

    dataset = Dataset.from_dict(data)

    print("Starting Ragas evaluation...")
    with mlflow.start_run():
        mlflow.log_param("model", "tinyllama")
        mlflow.log_param("embedding_model", "nomic-embed-text")

        results = evaluate(
            dataset=dataset,
            metrics=[
                context_precision,
                context_recall,
                faithfulness,
                answer_relevancy,
            ],
            llm=llm,
            embeddings=embeddings,
        )

        # Log Metrics
        print("Evaluation Result:", results)
        for metric, value in results.items():
            mlflow.log_metric(metric, value)

        # Save artifacts
        df = results.to_pandas()
        df.to_json("ragas_results.json", orient="records")
        mlflow.log_table(df, "eval_results.json")
        print("Evaluation complete. Results saved to ragas_results.json")


if __name__ == "__main__":
    run_evaluation()
