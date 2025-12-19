CREATE EXTENSION IF NOT EXISTS vector;

-- Create items table with embedding column in vectors schema
CREATE TABLE IF NOT EXISTS vectors.items (
    id BIGSERIAL PRIMARY KEY,
    content TEXT,
    embedding vector(384), -- Dimension for all-MiniLM-L6-v2 model
    metadata JSONB,
    file_id TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create HNSW Index for fast similarity search
CREATE INDEX IF NOT EXISTS items_embedding_idx ON vectors.items USING hnsw (embedding vector_l2_ops);
