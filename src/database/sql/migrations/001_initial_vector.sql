-- Enable pgvector extension TODO: try to pass collection name as an argument
CREATE EXTENSION IF NOT EXISTS vector;

-- Create items table with embedding column
-- This logic should match your application's entity definition
CREATE TABLE IF NOT EXISTS items (
    id BIGSERIAL PRIMARY KEY,
    content TEXT,
    embedding vector(3) -- Example dimension, should match model
);

-- Create HNSW Index
CREATE INDEX IF NOT EXISTS items_embedding_idx ON items USING hnsw (embedding vector_l2_ops);
