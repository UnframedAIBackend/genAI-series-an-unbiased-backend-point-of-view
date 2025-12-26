import os

import mlflow
from datasets import Dataset
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from ragas import evaluate
from ragas.metrics import (
    answer_relevancy,
    context_precision,
    context_recall,
    faithfulness,
)

# Configuration for Local LLM (Self-contained)
# We use LiteLLM (running on port 4000) which proxies to our local Ollama instance.
# This ensures we are NOT using OpenAI or any external API.
os.environ["OPENAI_API_KEY"] = "sk-1234"  # Dummy key required by client validation
os.environ["OPENAI_API_BASE"] = "http://localhost:4000"

# Initialize LLM & Embeddings
# Ragas uses these to judge the quality of the RAG pipeline.
llm = ChatOpenAI(
    model="ollama/tinyllama", # Match the model defined in docker-compose command
    temperature=0,
    openai_api_base="http://localhost:4000",
    openai_api_key="sk-1234"
)

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small", # LiteLLM can mock this or map to local embedding
    openai_api_base="http://localhost:4000",
    openai_api_key="sk-1234"
)

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
            "They help finding similar items based on meaning."
        ],
        [
            "HNSW is a graph-based indexing algorithm.",
            "IVF (Inverted File Index) clusters vectors to speed up search."
        ]
    ],
    "ground_truth": [
        "Vector databases allow for semantic search using high-dimensional vectors.",
        "HNSW is graph-based, IVF is cluster-based."
    ]
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

    with mlflow.start_run():
        mlflow.log_param("model", "tinyllama-local")

        print("Starting Ragas evaluation...")
        results = evaluate(
            dataset=dataset,
            metrics=[
                context_precision,
                context_recall,
                faithfulness,
                answer_relevancy,
            ],
            llm=llm,
            embeddings=embeddings
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
