import functools
import inspect
import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
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
        user: User = data.get("event_from_user")
        if user:
            unwrapped_handler = unwrap_handler(handler)
            throttling_key = getattr(unwrapped_handler, "throttling_key", None)
            throttling_rate = getattr(
                unwrapped_handler, "throttling_rate", self.default_rate
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


def unwrap_handler(handler):
    if isinstance(handler, functools.partial):
        handler = inspect.unwrap(handler).args[0]
        return unwrap_handler(handler)
    else:
        return inspect.unwrap(handler).__self__.callback


def rate_limit(key=None, rate=5):
    """Decorator for settling throttling key and rate for handler"""

    def decorator(func):
        setattr(func, "throttling_key", key)
        setattr(func, "throttling_rate", rate)
        return func

    return decorator
