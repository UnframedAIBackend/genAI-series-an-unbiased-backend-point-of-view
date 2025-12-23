db = db.getSiblingDB('mongo');

// 1. Create embeddings collection and indexes
const EMBEDDINGS_COLLECTION = "embeddings";
const EMBEDDINGS_PREFIX = `idx_${EMBEDDINGS_COLLECTION}_`;

db.createCollection(EMBEDDINGS_COLLECTION);

// Using a standard index for metadata lookups
db[EMBEDDINGS_COLLECTION].createIndex({ "file_id": 1 }, { "name": `${EMBEDDINGS_PREFIX}file_id` });

// Define Atlas Vector Search Index (Note: Only works on Atlas or supported versions)
// For local/generic compatibility, we document the intention.
try {
    db[EMBEDDINGS_COLLECTION].createSearchIndex("vector_index", {
        "definition": {
            "mappings": {
                "dynamic": true,
                "fields": {
                    "embedding": {
                        "dimensions": 384,
                        "similarity": "cosine",
                        "type": "knnVector"
                    }
                }
            }
        }
    });
    print('✓ Vector search index creation initiated');
} catch (e) {
    print('Found issue creating search index (likely non-Atlas env), creating standard index as fallback: ' + e.message);
    // Fallback index for basic operations
    db[EMBEDDINGS_COLLECTION].createIndex({ "embedding": 1 }, { "name": `${EMBEDDINGS_PREFIX}fallback` });
}

// 2. Create file_management collection and indexes
const FILE_MANAGEMENT_COLLECTION = "file_management";
const FILE_MANAGEMENT_PREFIX = `idx_${FILE_MANAGEMENT_COLLECTION}_`;
db.createCollection(FILE_MANAGEMENT_COLLECTION);
db[FILE_MANAGEMENT_COLLECTION].createIndex({ "workflow_id": 1 }, { "name": `${FILE_MANAGEMENT_PREFIX}workflow_id` });
db[FILE_MANAGEMENT_COLLECTION].createIndex({ "status": 1 }, { "name": `${FILE_MANAGEMENT_PREFIX}status` });

print('✓ MongoDB initialization completed successfully');
