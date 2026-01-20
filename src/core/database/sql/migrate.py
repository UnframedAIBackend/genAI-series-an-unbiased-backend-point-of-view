import asyncio
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import asyncpg

from src.core.configuration.configuration import config


class SQLMigrate:
    def __init__(self):
        self.migrations_dir = Path("src/core/database/sql/migrations")
        self.database_url = config.get("DATABASE_URL").replace("+asyncpg", "")

    async def run(self) -> None:
        db_engine = config.get("DATABASE_ENGINE")
        if db_engine not in ["postgres", "sql"]:
            print(f"Skipping SQL migrations. Current engine: {db_engine}")
            return

        print("Running SQL migrations...")

        if not self.migrations_dir.exists():
            print(f"Migrations directory not found: {self.migrations_dir}")
            return

        conn = await asyncpg.connect(self.database_url)
        try:
            for file in sorted(self.migrations_dir.glob("0*.py")):
                print(f"Running migration: {file.name}")
                module = self.__load_migration(file)
                await module.up(conn)
            print("✓ SQL Migrations completed successfully")
        except Exception as e:
            print(f"✗ SQL Migration failed: {e}")
            raise
        finally:
            await conn.close()

    def __load_migration(self, file: Path):
        spec = spec_from_file_location(file.stem, file)
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


if __name__ == "__main__":
    asyncio.run(SQLMigrate().run())
