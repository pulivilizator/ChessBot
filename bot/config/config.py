from environs import Env
from dataclasses import dataclass

@dataclass
class TgBot:
    token_bot: str

@dataclass
class DataBase:
    user: str
    passw: str
    host: str
    port: int
    db: str

@dataclass
class Config:
    tg_bot: TgBot
    data_base: DataBase


def get_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(tg_bot=TgBot(token_bot=env('BOT_TOKEN')),
                  data_base=DataBase(
                      user=env('C_USER'),
                      passw=env('PASSWORD'),
                      host=env('HOST'),
                      port=int(env('PORT')),
                      db=env('DATABASE')
                  ))
