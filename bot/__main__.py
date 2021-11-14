import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.client.session.middlewares.request_logging import RequestLogging
from aiogram.dispatcher.fsm.storage.redis import RedisStorage
from aiogram.methods import GetUpdates
from aiogram.types import BotCommand, BotCommandScopeDefault
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from bot.config_reader import load_config
from bot.db.utils import make_connection_string
from bot.handlers.game import register_game
from bot.handlers.stats import register_stats
from bot.middlewares import DBSession, RepoMiddleware, ThrottlingMiddleware

logger = logging.getLogger(__name__)


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command="start",
            description="Start new game",
        ),
        BotCommand(
            command="stats",
            description="Show personal statistics",
        ),
        BotCommand(
            command="stats_all",
            description="Show total statistics",
        ),
    ]

    await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    config = load_config()

    # Creating DB engine for PostgreSQL
    engine = create_async_engine(
        make_connection_string(config.db), future=True, echo=False
    )

    # Creating DB connections pool
    session_fabric = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    storage = RedisStorage.from_url(f"redis://{config.redis.host}")
    bot = Bot(config.bot.token)
    dp = Dispatcher(storage=storage, isolate_events=True)

    session_key = "session"
    bot.session.middleware(RequestLogging(ignore_methods=[GetUpdates]))

    dp.message.middleware(ThrottlingMiddleware())

    dp.message.outer_middleware(DBSession(session_fabric, session_key=session_key))
    dp.callback_query.outer_middleware(
        DBSession(session_fabric, session_key=session_key)
    )

    dp.message.outer_middleware(RepoMiddleware(session_key=session_key))
    dp.callback_query.outer_middleware(RepoMiddleware(session_key=session_key))

    dp.message.filter(F.chat.type == "private")
    dp.callback_query.filter(F.message.chat.type == "private")

    register_game(dp=dp)
    register_stats(dp=dp)

    try:
        await set_commands(bot)
        await bot.get_updates(offset=-1)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()
        await storage.close()


try:
    asyncio.run(main())
except (KeyboardInterrupt, SystemExit):
    logger.warning("Exit")
