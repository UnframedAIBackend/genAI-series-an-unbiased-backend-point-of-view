import asyncio
from pathlib import Path
import asyncpg
from src.core.configuration.configuration import config


class SQLMigrate:
    def __init__(self):
        self.migrations_dir = Path("src/database/sql/migrations")
        self.database_url = config.get("DATABASE_URL").replace("+asyncpg", "")
    
    async def run(self) -> None:
        print("Running migrations...")
        
        if not self.migrations_dir.exists():
            print(f"Migrations directory not found: {self.migrations_dir}")
            return
        
        conn = await asyncpg.connect(self.database_url)
        try:
            for file in sorted(self.migrations_dir.glob("*.sql")):
                print(f"Running migration: {file.name}")
                sql = file.read_text()
                await conn.execute(sql)
            print("✓ Migrations completed successfully")
        except Exception as e:
            print(f"✗ Migration failed: {e}")
            raise
        finally:
            await conn.close()


if __name__ == "__main__":
    migrate = SQLMigrate()
    asyncio.run(migrate.run())
