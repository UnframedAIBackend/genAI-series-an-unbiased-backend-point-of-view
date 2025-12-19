-- Create schemas for application and Temporal
-- This script runs on PostgreSQL initialization

-- Create Application schemas
CREATE SCHEMA IF NOT EXISTS app;
CREATE SCHEMA IF NOT EXISTS vectors;

-- Create Temporal schemas
CREATE SCHEMA IF NOT EXISTS temporal;
CREATE SCHEMA IF NOT EXISTS temporal_visibility;

-- Grant permissions to postgres user
GRANT ALL PRIVILEGES ON SCHEMA app TO postgres;
GRANT ALL PRIVILEGES ON SCHEMA vectors TO postgres;
GRANT ALL PRIVILEGES ON SCHEMA temporal TO postgres;
GRANT ALL PRIVILEGES ON SCHEMA temporal_visibility TO postgres;

-- Set search path to include all schemas
ALTER DATABASE postgres SET search_path TO app, vectors, temporal, temporal_visibility, public;

-- Comments for documentation
COMMENT ON SCHEMA app IS 'Main application data';
COMMENT ON SCHEMA vectors IS 'Vector embeddings and similarity search data';
COMMENT ON SCHEMA temporal IS 'Temporal persistence data';
COMMENT ON SCHEMA temporal_visibility IS 'Temporal visibility data';
