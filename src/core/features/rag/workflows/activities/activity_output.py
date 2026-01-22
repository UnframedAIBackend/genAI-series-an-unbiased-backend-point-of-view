from dataclasses import dataclass
from typing import List, TypedDict


class VectorMetadata(TypedDict, total=False):
    chunk_index: int
    total_chunks: int
    embedding_model: str
    original_filename: str
    file_size_bytes: int
    content_hash: str
    page_number: int
    author: str


@dataclass
class FileProcessingInput:
    file_id: str
    file_path: str
    original_filename: str
    chunk_strategy: str
    embedding_model: str
    db_engine: str
    indexing_strategy: str


@dataclass
class ChunkItem:
    content: str
    metadata: dict  # Changed from VectorMetadata to dict for better Temporal serialization

@dataclass
class ChunkData:
    strategy: str
    chunks: List[ChunkItem]
    file_id: str  # Add for easier batch processing


@dataclass
class BatchProcessingResult:
    """Result from processing and storing a batch of embeddings - only metadata, no large data"""
    batch_number: int
    chunks_processed: int
    vectors_stored: int
    embedding_model: str


@dataclass
class FileProcessingResult:
    file_id: str
    status: str
    chunks_count: int
    embeddings_count: int
    error_message: str | None = None
