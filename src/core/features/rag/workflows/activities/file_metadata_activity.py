from temporalio import activity
from datetime import datetime
from typing import Optional
import asyncpg
import os
from src.core.configuration.configuration import config


@activity.defn
async def store_file_metadata(
    file_id: str,
    original_filename: str,
    stored_filename: str,
    path: str,
    size: int,
    workflow_id: str,
    workflow_run_id: str
) -> bool:
    """
    Store file metadata in the database with workflow tracking.
    
    Args:
        file_id: Unique file identifier
        original_filename: Original name of the uploaded file
        stored_filename: Name used for storage
        path: Storage path
        size: File size in bytes
        workflow_id: Temporal workflow ID
        workflow_run_id: Temporal workflow run ID
        
    Returns:
        True if successful, raises exception otherwise
    """
    database_url = config.get("DATABASE_URL")
    
    conn = await asyncpg.connect(database_url)
    try:
        await conn.execute(
            """
            INSERT INTO app.file_management 
            (id, original_filename, store_filename, path, size, updated_at, status, workflow_id, workflow_run_id)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            ON CONFLICT (id) DO UPDATE SET
                workflow_id = EXCLUDED.workflow_id,
                workflow_run_id = EXCLUDED.workflow_run_id,
                updated_at = EXCLUDED.updated_at
            """,
            file_id,
            original_filename,
            stored_filename,
            path,
            size,
            datetime.now(),
            'pending',
            workflow_id,
            workflow_run_id
        )
        return True
    finally:
        await conn.close()
