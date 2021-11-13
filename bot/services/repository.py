import logging
from abc import ABC
from typing import Any, Callable, Dict, List, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db import models

logger = logging.getLogger(__name__)


class BaseRepo(ABC):
    repo_key: str

    def __init__(self, session: AsyncSession) -> None:
        self.session = session


class Repo(BaseRepo):
    repo_key = "repo"

    async def add_game_history_entry(self, game_history: models.GameHistoryEntry):
        async with self.session.begin():
            self.session.add(game_history)

    async def update_game_score(self, game_id: UUID, new_score: int) -> None:
        async with self.session.begin():
            game_history: Optional[models.GameHistoryEntry] = await self.session.get(
                models.GameHistoryEntry, game_id
            )
            if game_history:
                game_history.score = new_score
            else:
                logger.warning("Don`t find game with game id %s for update", game_id)

    async def user_top_scores(
        self, user_id: int
    ) -> Optional[List[models.GameHistoryEntry]]:
        async with self.session.begin():
            query = (
                select(models.GameHistoryEntry)
                .filter_by(telegram_id=user_id)
                .order_by(models.GameHistoryEntry.score.desc())
                .limit(5)
            )
            result = await self.session.execute(query)
            return result.scalars().all()

    async def users_count(self) -> int:
        async with self.session.begin():
            query = select(func.count()).select_from(
                select(models.GameHistoryEntry)
                .distinct(models.GameHistoryEntry.telegram_id)
                .subquery()
            )
            result = await self.session.execute(query)
            return result.scalar()

    async def all_users_top_scores(
        self, filters: Dict[str, Any]
    ) -> Optional[List[models.GameHistoryEntry]]:
        async with self.session.begin():
            query = (
                select(models.GameHistoryEntry)
                .filter_by(**filters)
                .order_by(models.GameHistoryEntry.score.desc())
                .limit(9)
            )
            result = await self.session.execute(query)
            return result.scalars().all()
