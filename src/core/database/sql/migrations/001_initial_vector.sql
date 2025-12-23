CREATE EXTENSION IF NOT EXISTS vector;

-- Create vector_store table with embedding column in vectors schema
CREATE TABLE IF NOT EXISTS vectors.vector_store (
    id BIGSERIAL PRIMARY KEY,
    content TEXT,
    embedding vector(384),
    metadata JSONB,
    file_id TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create HNSW Index for fast similarity search
CREATE INDEX IF NOT EXISTS vector_store_embedding_idx ON vectors.vector_store USING hnsw (embedding vector_l2_ops);
