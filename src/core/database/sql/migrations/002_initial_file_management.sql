--- Creating table for rag

BEGIN;

CREATE TYPE app.file_status AS ENUM ('pending', 'completed', 'failed');

DO $$
BEGIN
    CREATE TABLE IF NOT EXISTS app.file_management (
        id TEXT PRIMARY KEY NOT NULL,
        original_filename VARCHAR(255) NOT NULL,
        store_filename TEXT NOT NULL,
        path TEXT NOT NULL,
        size INT NOT NULL,
        updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
        status app.file_status NOT NULL DEFAULT 'pending',
        workflow_id TEXT,
        workflow_run_id TEXT,
        error_message TEXT
    );

    -- Create indexes for workflow lookups
    CREATE INDEX IF NOT EXISTS idx_file_management_workflow_id ON app.file_management(workflow_id);
    CREATE INDEX IF NOT EXISTS idx_file_management_status ON app.file_management(status);
    EXCEPTION
        WHEN OTHERS THEN
            ROLLBACK;
            RAISE;
END $$;

COMMIT;
