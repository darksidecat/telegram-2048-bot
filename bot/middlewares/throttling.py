import functools
import inspect
import logging
from typing import Any, Awaitable, Callable, Dict, Optional

from aiogram import BaseMiddleware
from aiogram.dispatcher.event.handler import HandlerObject
from aiogram.types import TelegramObject, User
from aiolimiter import AsyncLimiter

logger = logging.getLogger(__name__)


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, default_rate: int = 2) -> None:
        self.limiters: Dict[str, AsyncLimiter] = {}
        self.default_rate = default_rate

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user: Optional[User] = data.get("event_from_user")
        if user:
            # get the real handler that will be called at the end of chain
            real_handler: HandlerObject = data.get("handler")

            # get settled throttling flags from handler
            throttling_key = real_handler.flags.get("throttling_key", None)
            throttling_rate = real_handler.flags.get(
                "throttling_rate", self.default_rate
            )

            if throttling_key:
                limiter = self.limiters.setdefault(
                    f"{user.id}:{throttling_key}", AsyncLimiter(1, throttling_rate)
                )

                if limiter.has_capacity():
                    async with limiter:
                        return await handler(event, data)
                else:
                    logger.info(
                        "Throttled for user=%d, key=%s, rate=%d",
                        user.id,
                        throttling_key,
                        throttling_rate,
                    )
            else:
                return await handler(event, data)

        else:
            return await handler(event, data)
