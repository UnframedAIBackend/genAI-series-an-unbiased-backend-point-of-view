db = db.getSiblingDB('mongo');

// TODO: try to pass collection name as an argument
db.createCollection();

db.chonkie.createIndex(
    { embedding: "2dsphere" },
    { name: "vector_index" }
);

print('✓ Vector index created successfully');
