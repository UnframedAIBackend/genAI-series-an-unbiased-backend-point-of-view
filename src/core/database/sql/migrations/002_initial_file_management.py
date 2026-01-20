TABLE_NAME = "app.file_management"


async def up(conn) -> None:
    await conn.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'file_status') THEN
                CREATE TYPE app.file_status AS ENUM ('pending', 'completed', 'failed');
            END IF;
        END $$;
    """)

    await conn.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
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
    """)
    print(f"Created table: {TABLE_NAME}")

    await conn.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_file_management_workflow_id ON {TABLE_NAME}(workflow_id);
    """)
    await conn.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_file_management_status ON {TABLE_NAME}(status);
    """)
    print("✓ Created indexes for file_management")


async def down(conn) -> None:
    await conn.execute(f"DROP TABLE IF EXISTS {TABLE_NAME};")
    await conn.execute("DROP TYPE IF EXISTS app.file_status;")
    print(f"Dropped table: {TABLE_NAME}")
