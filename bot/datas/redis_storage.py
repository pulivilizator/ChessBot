import asyncio

from aiogram.fsm.storage.redis import RedisStorage
from redis import asyncio as aioredis
import pickle

async def memory_storage() -> RedisStorage:
    redis = await aioredis.Redis()
    storage = RedisStorage(redis)
    return storage


class RedisBattleStorage:
    __instance = None
    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self):
        self.redis = aioredis.Redis(db=1)

class OnlineStorage(RedisBattleStorage):
    @property
    async def battle_games(self):
        battle_games = await self.redis.smembers('battle_games')

        return map(lambda x: pickle.loads(x) if x != b'0' else x, battle_games)

    @property
    async def battle_games_offline(self):
        battle_games = await self.redis.smembers('battle_games_offline')

        return map(lambda x: pickle.loads(x) if x != b'0' else x, battle_games)

    async def add(self, data):
        await self.redis.sadd('battle_games', pickle.dumps(data))

    async def add_off(self, data):
        await self.redis.sadd('battle_games_offline', pickle.dumps(data))

    async def set_key(self, key, value):
        await self.redis.rpush(key, value)

    async def get_key(self, key):
        return await self.redis.lrange(key, 0, -1)

    async def del_key(self, key):
        await self.redis.delete(key)

    async def overwriting(self, games):
        await self.redis.delete('battle_games')
        for game in games:
            await self.redis.sadd('battle_games', pickle.dumps(game))

class OfflineStorage(RedisBattleStorage):

    @property
    async def battle_games_offline(self):
        battle_games = await self.redis.smembers('battle_games_offline')

        return map(lambda x: pickle.loads(x) if x != b'0' else x, battle_games)


    async def add_off(self, data):
        await self.redis.sadd('battle_games_offline', pickle.dumps(data))

    async def set_key(self, key, value):
        await self.redis.rpush(key, value)

    async def get_key(self, key):
        return await self.redis.lrange(key, 0, -1)

    async def del_key(self, key):
        await self.redis.delete(key)

    async def overwriting_off(self, games):
        await self.redis.delete('battle_games_offline')
        for game in games:
            await self.redis.sadd('battle_games_offline', pickle.dumps(game))


storage = OnlineStorage()
offline_storage = OfflineStorage()