from pymongo import AsyncMongoClient

async def up(db):
    """
    Setup initial vector collection and search index for MongoDB.
    """
    collection_name = "embeddings"
    
    # Create the collection if it doesn't exist
    collections = await db.list_collection_names()
    if collection_name not in collections:
        await db.create_collection(collection_name)
        print(f"Created collection: {collection_name}")

    # Create Atlas Vector Search Index
    # Note: Search indexes can usually only be created on Atlas or with specific local setups.
    # We define the index structure here.
    search_index_name = "vector_index"
    
    # Check existing search indexes
    cursor = db[collection_name].list_search_indexes()
    existing_indexes = await cursor.to_list(length=100)
    
    if not any(idx.get("name") == search_index_name for idx in existing_indexes):
        print(f"Defining search index: {search_index_name}")
        search_index_definition = {
            "name": search_index_name,
            "definition": {
                "mappings": {
                    "dynamic": True,
                    "fields": {
                        "embedding": {
                            "dimensions": 384, # Dimension for all-MiniLM-L6-v2 model
                            "similarity": "cosine",
                            "type": "knnVector"
                        }
                    }
                }
            }
        }
        
        try:
            await db[collection_name].create_search_index(model=search_index_definition)
            print(f"✓ Search index creation initiated: {search_index_name}")
        except Exception as e:
            # On some environments like local mongo, create_search_index might fail
            print(f"Warning: Could not create search index (might be unsupported in this env): {e}")

async def down(db):
    """
    Rollback migration.
    """
    await db.drop_collection("embeddings")
    print("Dropped collection: embeddings")
