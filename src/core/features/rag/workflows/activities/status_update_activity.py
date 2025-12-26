from typing import Optional

from temporalio import activity

from src.core.container.container import container


@activity.defn
async def update_file_status(file_id: str, status: str, error_message: Optional[str] = None) -> None:
    """
    Activity to update the processing status of a file.
    """
    file_management_repository = container.file_management_repository()

    file_record = await file_management_repository.find_by_id(file_id)
    if file_record:
        file_record.status = status
        await file_management_repository.update(file_id, file_record)

    activity.logger.info(f"Updated file {file_id} status to {status}")
