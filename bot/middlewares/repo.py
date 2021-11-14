from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession

from bot.services.repository import Repos

REPO_KEY = "repo"


class RepoMiddleware(BaseMiddleware):
    def __init__(self, session_key: str) -> None:
        self.session_key = session_key

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:

        session: AsyncSession = data[self.session_key]
        data[REPO_KEY] = Repos(session)

        result = await handler(event, data)

        data.pop(REPO_KEY)
        return result
