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
        if obj is None:
            return self
        try:
            return getattr(obj, self.private_repo_key)
        except AttributeError:
            repo = self.repo(obj.session)
            setattr(obj, self.private_repo_key, repo)
            return repo

    def __set_name__(self, obj, name):
        self.private_repo_key = "_" + name


class Repos:
    game = Repo(GameRepo)

    def __init__(self, session: AsyncSession):
        self.session = session

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
