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
        if cls.__instance in None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self):
        self.redis = redis = aioredis.Redis(db=1)
        if not await redis.exists('battle_games'):
            await redis.sadd('battle_games', '0')
            await redis.srem('battle_games', '0')


    @property
    async def battle_games(self):
        battle_games = await self.redis.smembers('battle_games')

        return map(lambda x: pickle.loads(x) if x != b'0' else x, battle_games)

    async def add(self, data):
        await self.redis.sadd('battle_games', pickle.dumps(data))

