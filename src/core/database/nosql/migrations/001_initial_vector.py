from src.core.configuration.configuration import config

COLLECTION_NAME = "vector_store"

async def up(db):

    collections = await db.list_collection_names()
    if COLLECTION_NAME not in collections:
        await db.create_collection(COLLECTION_NAME)
        print(f"Created collection: {COLLECTION_NAME}")

    await db[COLLECTION_NAME].create_index([("file_id", 1)], name="idx_embeddings_file_id")

    search_index_name = "vector_index"

    search_index_definition = {
        "name": search_index_name,
        "definition": {
            "mappings": {
                "dynamic": True,
                "fields": {
                    config.get("VECTOR_FIELD_NAME"): {
                        "dimensions": config.get("VECTOR_DIMENSION"),
                        "similarity": config.get("VECTOR_SIMILARITY"),
                        "type": config.get("VECTOR_SIMILARITY_TYPE"),
                    }
                },
            }
        },
    }

    try:
        await db[COLLECTION_NAME].create_search_index(model=search_index_definition)
        print(f"✓ Search index creation initiated: {search_index_name}")
    except Exception:
        await db[COLLECTION_NAME].create_index([(config.get("VECTOR_FIELD_NAME"), 1)], name="idx_embeddings_fallback")
        print("✓ Standard fallback index created")


async def down(db):
    await db.drop_collection(COLLECTION_NAME)
    print("Dropped collection: embeddings")
