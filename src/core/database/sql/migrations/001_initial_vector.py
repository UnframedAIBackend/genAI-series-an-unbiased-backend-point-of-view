from src.core.configuration.configuration import config

TABLE_NAME = "vectors.vector_store"


async def up(conn) -> None:
    await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    dimension = config.get("VECTOR_DIMENSION")

    await conn.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id BIGSERIAL PRIMARY KEY,
            content TEXT,
            embedding vector({dimension}),
            metadata JSONB,
            file_id TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)
    print(f"Created table: {TABLE_NAME}")

    await conn.execute(f"""
        CREATE INDEX IF NOT EXISTS vector_store_embedding_idx
        ON {TABLE_NAME} USING hnsw (embedding vector_l2_ops);
    """)
    print("✓ Created HNSW index for vector similarity search")


async def down(conn) -> None:
    await conn.execute(f"DROP TABLE IF EXISTS {TABLE_NAME};")
    print(f"Dropped table: {TABLE_NAME}")
