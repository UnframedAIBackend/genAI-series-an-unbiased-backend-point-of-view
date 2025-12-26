
async def up(db):

    collection_name = "embeddings"

    collections = await db.list_collection_names()
    if collection_name not in collections:
        await db.create_collection(collection_name)
        print(f"Created collection: {collection_name}")

    await db[collection_name].create_index([("file_id", 1)], name="idx_embeddings_file_id")

    search_index_name = "vector_index"

    search_index_definition = {
        "name": search_index_name,
        "definition": {
            "mappings": {
                "dynamic": True,
                "fields": {
                    "embedding": {
                        "dimensions": 384,
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
    except Exception:
        await db[collection_name].create_index([("embedding", 1)], name="idx_embeddings_fallback")
        print("✓ Standard fallback index created")

async def down(db):
    await db.drop_collection("embeddings")
    print("Dropped collection: embeddings")
