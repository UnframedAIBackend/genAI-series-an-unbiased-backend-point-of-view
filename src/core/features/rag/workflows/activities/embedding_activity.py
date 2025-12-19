from temporalio import activity
from typing import List
from sentence_transformers import SentenceTransformer

from src.core.features.rag.workflows.models import ChunkData, EmbeddingData


@activity.defn
async def generate_embeddings(chunks: List[ChunkData], embedding_model: str) -> List[EmbeddingData]:
    """
    Generate embeddings for text chunks using the specified model.
    
    Args:
        chunks: List of chunk data to embed
        embedding_model: Model identifier to use for embeddings
        
    Returns:
        List of embedding data with vectors and metadata
    """
    # Load the embedding model
    model = SentenceTransformer(embedding_model)
    
    # Extract text content from chunks
    texts = [chunk.content for chunk in chunks]
    
    # Generate embeddings in batch
    embeddings = model.encode(texts, show_progress_bar=False)
    
    # Create EmbeddingData objects
    embedding_data_list = []
    for chunk, embedding in zip(chunks, embeddings):
        embedding_data = EmbeddingData(
            chunk_id=chunk.chunk_id,
            embedding=embedding.tolist(),
            metadata={
                **chunk.metadata,
                'embedding_model': embedding_model,
                'embedding_dim': len(embedding)
            }
        )
        embedding_data_list.append(embedding_data)
    
    activity.logger.info(
        f"Generated {len(embedding_data_list)} embeddings using {embedding_model} "
        f"(dim: {len(embeddings[0])})"
    )
    
    return embedding_data_list
