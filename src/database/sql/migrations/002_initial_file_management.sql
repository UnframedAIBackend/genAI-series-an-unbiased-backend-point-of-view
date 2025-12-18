--- Creating table for rag

BEGIN;

DO $$
BEGIN
    CREATE TABLE IF NOT EXISTS file_management (
        id TEXT PRIMARY KEY NOT NULL,
        original_filename VARCHAR(255) NOT NULL,
        store_filename TEXT NOT NULL,
        path TEXT NOT NULL,
        size INT NOT NULL,
        updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
        status VARCHAR(255) NOT NULL DEFAULT 'pending'
    );
    EXCEPTION
        WHEN OTHERS THEN
            ROLLBACK;
            RAISE;
END $$;

COMMIT;