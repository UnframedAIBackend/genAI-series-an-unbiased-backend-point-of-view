from typing import List

from src.core.database.database_engine import DatabaseEngine
from src.core.database.i_repository import IVectorRepository
from src.core.database.nosql.nosql_repository import NoSQLRepository, T
from src.core.database.repository_registry import repository_registry


class NoSQLVectorRepository(NoSQLRepository[T], IVectorRepository[T]):
    async def similarity_search(self, query_vector: List[float], limit: int = 5) -> List[dict]:
        pipeline = [
            {
                "$vectorSearch": {
                    "index": "vector_index",
                    "path": "embedding",
                    "queryVector": query_vector,
                    "numCandidates": limit * 10,
                    "limit": limit,
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "id": {"$toString": "$_id"},
                    "file_id": 1,
                    "content": 1,
                    "metadata": 1,
                    "score": {"$meta": "vectorSearchScore"},
                }
            },
        ]
        results = []
        cursor = await self.collection.aggregate(pipeline)
        async for doc in cursor:
            results.append(doc)
        return results


repository_registry.register(f"{DatabaseEngine.NOSQL.value}_vector", NoSQLVectorRepository)
