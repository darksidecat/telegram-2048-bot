from typing import Any, Awaitable, Callable, Dict, Iterable, Type

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from bot.services.repository import RepoProtocol


class RepoMiddleware(BaseMiddleware):
    def __init__(self, repos: Iterable[Type[RepoProtocol]], session_key: str) -> None:
        self.repos = repos
        self.session_key = session_key

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:

        session = data.get(self.session_key)

        repo_keys = []
        for repo in self.repos:
            data[repo.repo_key] = repo(session)
            repo_keys.append(repo.repo_key)

        result = await handler(event, data)

        for repo_key in repo_keys:
            data.pop(repo_key)

        return result
