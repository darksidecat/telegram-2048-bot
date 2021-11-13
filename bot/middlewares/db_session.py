from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.orm import sessionmaker


class DBSession(BaseMiddleware):
    def __init__(self, sm: sessionmaker, session_key: str) -> None:
        self.session = sm
        self.session_key = session_key

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:

        async with self.session() as session:
            data[self.session_key] = session

            result = await handler(event, data)

            data.pop(self.session_key)
            return result
