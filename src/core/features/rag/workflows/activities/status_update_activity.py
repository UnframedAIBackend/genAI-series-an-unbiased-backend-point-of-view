from temporalio import activity
from datetime import datetime
import asyncpg
import os
from src.core.configuration.configuration import config


@activity.defn
async def update_file_status(file_id: str, status: str, error_message: str | None = None) -> bool:
    """
    Update the processing status of a file in the database.
    
    Args:
        file_id: File identifier
        status: New status (pending, completed, failed)
        error_message: Optional error message if status is failed
        
    Returns:
        True if successful
    """
    database_url = config.get("DATABASE_URL")
    
    conn = await asyncpg.connect(database_url)
    try:
        await conn.execute(
            """
            UPDATE app.file_management
            SET status = $1::app.file_status,
                updated_at = $2,
                error_message = $3
            WHERE id = $4
            """,
            status,
            datetime.now(),
            error_message,
            file_id
        )
        
        activity.logger.info(f"Updated file {file_id} status to {status}")
        return True
    finally:
        await conn.close()
