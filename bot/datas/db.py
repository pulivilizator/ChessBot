import asyncpg
import asyncio
from config.config import get_config


class DataBase:
    __instance = None
    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self):
        self._config = get_config()
        self.connection = None

    async def connect(self):
        self.connection = await asyncpg.connect(
            host=self._config.data_base.host,
            port=self._config.data_base.port,
            user=self._config.data_base.user,
            password=self._config.data_base.passw,
            database=self._config.data_base.db
        )

    async def execute(self, query, *args):
        if self.connection is None:
            await self.connect()
        return await self.connection.execute(query, *args)

    async def fetch(self, query, *args):
        if self.connection is None:
            await self.connect()
        return await self.connection.fetch(query, *args)

    async def table_exists(self, table_name: str) -> bool:
        if self.connection is None:
            await self.connect()
        query = '''
              SELECT EXISTS (
                  SELECT 1
                  FROM pg_catalog.pg_tables
                  WHERE tablename = $1
              );
          '''
        return await self.connection.fetchval(query, table_name)

    async def create_table(self, table_name: str):
        if self.connection is None:
            await self.connect()
        if not await self.table_exists(table_name):
            query = f"""CREATE TABLE {table_name} (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(150),
                        user_id INT,
                        wins SMALLINT,
                        count_games SMALLINT,
                        leave SMALLINT);"""
            await self.execute(query)

    async def close(self):
        if self.connection is not None:
            await self.connection.close()
            self.connection = None

client = DataBase()