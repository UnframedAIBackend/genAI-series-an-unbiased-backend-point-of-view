from typing import List

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.database_engine import DatabaseEngine
from src.core.database.i_repository import IVectorRepository
from src.core.database.repository_registry import repository_registry
from src.core.database.sql.sql_repository import SQLRepository, T


class SQLVectorRepository(SQLRepository[T], IVectorRepository[T]):
    async def similarity_search(self, query_vector: List[float], limit: int = 5) -> List[T]:
        # Using pgvector distance operator <=> for cosine distance (1 - cosine similarity)
        vector_str = f"[{','.join(map(str, query_vector))}]"
        sql = text(
            f"SELECT *, (embedding <=> :vector) as score FROM {self.full_table_name} "
            f"ORDER BY embedding <=> :vector LIMIT :limit"
        )
        async with AsyncSession(self.engine) as session:
            result = await session.execute(sql, {"vector": vector_str, "limit": limit})
            mappings = result.mappings().all()
            return [{**m, "score": 1 - m["score"]} for m in mappings]


repository_registry.register(f"{DatabaseEngine.SQL.value}_vector", SQLVectorRepository)
