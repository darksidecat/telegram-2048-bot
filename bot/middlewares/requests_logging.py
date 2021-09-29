import logging
from typing import Awaitable, Callable, Optional, TypeVar

from aiogram import Bot
from aiogram.dispatcher.fsm.storage.base import BaseStorage
from aiogram.methods import Response, SendMessage, TelegramMethod
from aiogram.types import Chat, Message, User

logger = logging.getLogger(__name__)

T = TypeVar("T")


class RequestLogging:
    async def __call__(
        self,
        bot: Bot,
        method: TelegramMethod[T],
        make_request: Callable[[Bot, TelegramMethod[T]], Awaitable[Response[T]]],
    ):

        logger.info("Make request. Method: %s", type(method).__name__)
        return await make_request(bot, method)
