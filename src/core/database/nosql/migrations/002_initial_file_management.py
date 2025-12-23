import pymongo

async def up(db):
    """
    Setup file management collection and indexes for MongoDB.
    """
    collection_name = "file_management"
    
    # Create the collection if it doesn't exist
    collections = await db.list_collection_names()
    if collection_name not in collections:
        await db.create_collection(collection_name)
        print(f"Created collection: {collection_name}")

    # Create indexes for business logic lookups
    print(f"Creating indexes for collection: {collection_name}")
    
    # 1. Index on workflow_id for fast lookups
    await db[collection_name].create_index(
        [("workflow_id", pymongo.ASCENDING)],
        name="idx_file_management_workflow_id",
        background=True
    )

    # 2. Index on status for filtering
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
