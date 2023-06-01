from environs import Env
from dataclasses import dataclass

@dataclass
class TgBot:
    token_bot: str

@dataclass
class DataBase:
    login: str = False
    passw: str = False
    ip: str = False
    port: str = False

@dataclass
class Config:
    tg_bot: TgBot
    data_base: DataBase


def get_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(tg_bot=TgBot(token_bot=env('BOT_TOKEN')),
                  data_base=DataBase())
