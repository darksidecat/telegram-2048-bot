from dataclasses import dataclass
from os import getenv


@dataclass
class Bot:
    token: str


@dataclass
class DB:
    host: str
    port: int
    name: str
    login: str
    password: str


@dataclass
class Redis:
    host: str


@dataclass
class Config:
    bot: Bot
    db: DB
    redis: Redis


def load_config():
    return Config(
        bot=Bot(
            token=getenv("BOT_TOKEN"),
        ),
        db=DB(
            host=getenv("DB_HOST"),
            port=int(getenv("DB_PORT")),
            name=getenv("DB_NAME"),
            login=getenv("DB_USER"),
            password=getenv("DB_PASS"),
        ),
        redis=Redis(host=getenv("REDIS_HOST")),
    )
