from dataclasses import asdict, is_dataclass
from typing import Any, List, Optional, TypeVar

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from src.core.configuration.configuration import config
from src.core.database.database_engine import DatabaseEngine
from src.core.database.i_repository import IRepository
from src.core.database.repository_registry import repository_registry

T = TypeVar("T")


class SQLRepository(IRepository[T]):
    def __init__(self, table_name: str, schema: Optional[str] = None):
        self.table_name = table_name
        self.schema = schema
        self.engine = create_async_engine(config.get("DATABASE_URL"))

    @property
    def full_table_name(self) -> str:
        return f"{self.schema}.{self.table_name}" if self.schema else self.table_name

    async def find_all(self) -> List[T]:
        async with AsyncSession(self.engine) as session:
            result = await session.execute(text(f"SELECT * FROM {self.full_table_name}"))
            return result.mappings().all()

    async def create(self, data: Any) -> Any:
        # Convert to dict if it's a dataclass
        doc = asdict(data) if is_dataclass(data) else dict(data)

        columns = ", ".join(doc.keys())
        values = ", ".join([f":{k}" for k in doc.keys()])
        sql = text(f"INSERT INTO {self.full_table_name} ({columns}) VALUES ({values}) RETURNING *")

        async with AsyncSession(self.engine) as session:
            result = await session.execute(sql, doc)
            await session.commit()
            return result.mappings().first()

    async def create_many(self, data: List[Any]) -> List[Any]:
        if not data:
            return []

        # Convert each item to dict if it's a dataclass
        docs = [asdict(item) if is_dataclass(item) else dict(item) for item in data]

        columns = ", ".join(docs[0].keys())
        values = ", ".join([f":{k}" for k in docs[0].keys()])
        sql = text(f"INSERT INTO {self.full_table_name} ({columns}) VALUES ({values}) RETURNING *")

        async with AsyncSession(self.engine) as session:
            result = await session.execute(sql, docs)
            await session.commit()
            return result.mappings().all()

    async def find_by_id(self, id: int) -> Optional[T]:
        async with AsyncSession(self.engine) as session:
            result = await session.execute(text(f"SELECT * FROM {self.full_table_name} WHERE id = :id"), {"id": id})
            return result.mappings().first()

    async def update(self, id: int, data: dict) -> Optional[T]:
        set_clause = ", ".join([f"{k} = :{k}" for k in data.keys()])
        sql = text(f"UPDATE {self.full_table_name} SET {set_clause} WHERE id = :id RETURNING *")
        data["id"] = id

        async with AsyncSession(self.engine) as session:
            result = await session.execute(sql, data)
            await session.commit()
            return result.mappings().first()

    async def delete(self, id: int) -> bool:
        async with AsyncSession(self.engine) as session:
            result = await session.execute(text(f"DELETE FROM {self.full_table_name} WHERE id = :id"), {"id": id})
            await session.commit()
            return result.rowcount > 0


repository_registry.register(DatabaseEngine.SQL, SQLRepository)
