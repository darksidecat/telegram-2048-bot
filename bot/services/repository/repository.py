import logging
from functools import lru_cache
from typing import Type, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from bot.services.repository.base_repository import BaseSQLAlchemyRepo

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseSQLAlchemyRepo)


class SQLAlchemyRepos:
    def __init__(self, session: AsyncSession):
        self._session = session

    @lru_cache()  # @cache usage break typehints :(
    def get_repo(self, repo: Type[T]) -> T:
        return repo(self._session)

    async def commit(self):
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()
