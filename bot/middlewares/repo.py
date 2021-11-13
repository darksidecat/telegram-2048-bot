from typing import Any, Awaitable, Callable, Dict, Iterable, Type

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession

from bot.services.repository import BaseRepo


class RepoMiddleware(BaseMiddleware):
    def __init__(self, repos: Iterable[Type[BaseRepo]], session_key: str) -> None:
        self.repos = repos
        self.session_key = session_key

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:

        session: AsyncSession = data[self.session_key]

        repo_keys = []
        for repo in self.repos:
            data[repo.repo_key] = repo(session)
            repo_keys.append(repo.repo_key)

        result = await handler(event, data)

        for repo_key in repo_keys:
            data.pop(repo_key)

        return result
