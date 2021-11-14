import logging
from typing import Any, Type, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from bot.services.repository.game_repository import GameRepo

logger = logging.getLogger(__name__)

T = TypeVar("T")


class Repo:
    def __init__(self, repo: Type[T]):
        self.repo = repo

    def __get__(self, obj, owner: Any) -> T:
        repo = getattr(obj, self.repo_key)
        if repo:
            return repo
        repo = self.repo(obj.session)
        setattr(obj, self.repo_key, repo)
        return repo

    def __set_name__(self, name, owner):
        self.repo_key = name


class Repos:
    game = Repo(GameRepo)

    def __init__(self, session: AsyncSession):
        self.session = session

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
