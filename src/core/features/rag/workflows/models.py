from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class FileProcessingInput:
    """Input data for file processing workflow"""
    file_id: str
    file_path: str
    original_filename: str
    chunk_strategy: str
    embedding_model: str
    db_engine: str
    indexing_strategy: str


@dataclass
class ChunkData:
    """Data structure for file chunks"""
    chunk_id: str
    content: str
    metadata: Dict[str, Any]


@dataclass
class EmbeddingData:
    """Data structure for embeddings"""
    chunk_id: str
    embedding: List[float]
    metadata: Dict[str, Any]


@dataclass
class FileProcessingResult:
    """Result of file processing workflow"""
    file_id: str
    status: str
    chunks_count: int
    embeddings_count: int
    error_message: str | None = None
