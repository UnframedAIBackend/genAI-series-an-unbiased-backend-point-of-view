import pymongo


async def up(db):
    collection_name = "file_management"

    collections = await db.list_collection_names()
    if collection_name not in collections:
        await db.create_collection(collection_name)
        print(f"Created collection: {collection_name}")

    print(f"Creating indexes for collection: {collection_name}")

    await db[collection_name].create_index(
        [("workflow_id", pymongo.ASCENDING)],
        name="idx_file_management_workflow_id",
        background=True
    )

    await db[collection_name].create_index(
        [("status", pymongo.ASCENDING)],
        name="idx_file_management_status",
        background=True
    )

    print("✓ File management indexes created successfully")

async def down(db):
    """
    Rollback migration.
    """
    await db.drop_collection("file_management")
    print("Dropped collection: file_management")
