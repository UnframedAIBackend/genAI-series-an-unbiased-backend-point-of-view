from temporalio import activity
from typing import List
import os
import asyncpg
from pymongo import AsyncMongoClient
from src.core.configuration.configuration import config

from src.core.features.rag.workflows.models import EmbeddingData


@activity.defn
async def store_vectors(
    embeddings: List[EmbeddingData],
    db_engine: str,
    indexing_strategy: str,
    file_id: str
) -> int:
    """
    Store vector embeddings in the database using the specified engine and indexing strategy.
    
    Args:
        embeddings: List of embedding data to store
        db_engine: Database engine to use (sql, nosql)
        indexing_strategy: Indexing strategy (hnsw, ivfflat, graph)
        file_id: File identifier for grouping
        
    Returns:
        Number of embeddings stored
    """
    if db_engine == "sql":
        return await _store_vectors_sql(embeddings, indexing_strategy, file_id)
    elif db_engine == "nosql":
        return await _store_vectors_nosql(embeddings, indexing_strategy, file_id)
    else:
        raise ValueError(f"Unsupported database engine: {db_engine}")


async def _store_vectors_sql(
    embeddings: List[EmbeddingData],
    indexing_strategy: str,
    file_id: str
) -> int:
    """Store vectors in PostgreSQL with pgvector"""
    database_url = config.get("DATABASE_URL")
    
    conn = await asyncpg.connect(database_url)
    try:
        count = 0
        for emb in embeddings:
            # Convert embedding list to pgvector format
            embedding_str = f"[{','.join(map(str, emb.embedding))}]"
            
            await conn.execute(
                """
                INSERT INTO vectors.items (content, embedding, metadata, file_id)
                VALUES ($1, $2::vector, $3, $4)
                """,
                emb.metadata.get('content', ''),
                embedding_str,
                str(emb.metadata),
                file_id
            )
            count += 1
        
        activity.logger.info(f"Stored {count} vectors in PostgreSQL using {indexing_strategy} index")
        return count
    finally:
        await conn.close()


async def _store_vectors_nosql(
    embeddings: List[EmbeddingData],
    indexing_strategy: str,
    file_id: str
) -> int:
    """Store vectors in MongoDB with vector search"""
    mongo_url = config.get("DATABASE_URL")
    
    client = AsyncMongoClient(mongo_url)
    try:
        db = client.get_database()
        collection = db['embeddings']
        
        documents = []
        for emb in embeddings:
            doc = {
                'chunk_id': emb.chunk_id,
                'embedding': emb.embedding,
                'metadata': emb.metadata,
                'file_id': file_id,
                'indexing_strategy': indexing_strategy
            }
            documents.append(doc)
        
        result = await collection.insert_many(documents)
        count = len(result.inserted_ids)
        
        activity.logger.info(f"Stored {count} vectors in MongoDB using {indexing_strategy} index")
        return count
    finally:
        client.close()
