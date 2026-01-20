from dataclasses import dataclass
from typing import Any


@dataclass
class EnvVarSchema:
    required: bool
    type: type
    default: Any = None


ENV_SCHEMA: dict[str, EnvVarSchema] = {
    "DATABASE_URL": EnvVarSchema(required=True, type=str),
    "HF_TOKEN": EnvVarSchema(required=True, type=str),
    "TEMPORAL_HOST": EnvVarSchema(required=True, type=str),
    "CHUNK_OVERLAP": EnvVarSchema(required=False, type=int, default=200),
    "CHUNK_SIZE": EnvVarSchema(required=False, type=int, default=2048),
    "CHUNK_STRATEGY": EnvVarSchema(required=False, type=str, default="vanilla"),
    "DATABASE_ENGINE": EnvVarSchema(required=False, type=str, default="mongodb"),
    "EMBEDDING_MODEL": EnvVarSchema(required=False, type=str, default="vanilla"),
    "EMBEDDING_MODEL_CHUNK": EnvVarSchema(required=False, type=str, default="all-MiniLM-L6-v2"),
    "FILE_STORAGE_VENDOR": EnvVarSchema(required=False, type=str, default="local"),
    "LOG_LEVEL": EnvVarSchema(required=False, type=str, default="INFO"),
    "NODE_ENV": EnvVarSchema(required=False, type=str, default="development"),
    "PORT": EnvVarSchema(required=False, type=int, default=8000),
    "TEMPORAL_NAMESPACE": EnvVarSchema(required=False, type=str, default="default"),
    "TEMPORAL_TASK_QUEUE": EnvVarSchema(required=False, type=str, default="file-processing-queue"),
    "TZ": EnvVarSchema(required=False, type=str, default="America/Bogota"),
    "UPLOADS_PATH": EnvVarSchema(required=False, type=str, default="uploads"),
    "OLLAMA_HOST": EnvVarSchema(required=False, type=str, default="http://localhost:11434"),
    "GENERATION_MODEL": EnvVarSchema(required=False, type=str, default="ollama/tinyllama"),
    "VECTOR_DIMENSION": EnvVarSchema(required=False, type=int, default=768),
    "VECTOR_FIELD_NAME": EnvVarSchema(required=False, type=str, default="embedding"),
    "VECTOR_SIMILARITY": EnvVarSchema(required=False, type=str, default="cosine"),
    "VECTOR_SIMILARITY_TYPE": EnvVarSchema(required=False, type=str, default="knnVector"),
}
