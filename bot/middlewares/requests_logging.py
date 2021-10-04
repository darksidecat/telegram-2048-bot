import logging
from typing import Awaitable, Callable, TypeVar

from aiogram import Bot
from aiogram.methods import GetUpdates, Response, TelegramMethod

logger = logging.getLogger(__name__)

T = TypeVar("T")


class RequestLogging:
    def __init__(self, ignore_get_updates: bool = True):
        self.ignore_get_updates = ignore_get_updates

    async def __call__(
        self,
        bot: Bot,
        method: TelegramMethod[T],
        make_request: Callable[[Bot, TelegramMethod[T]], Awaitable[Response[T]]],
    ):
        if not self.ignore_get_updates or not isinstance(method, GetUpdates):
            logger.info(
                "Make request with method=%s by bot id=%d",
                method.__class__.__name__,
                bot.id,
            )
        return await make_request(bot, method)
