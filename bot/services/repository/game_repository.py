import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import func, select

from bot.db import models
from bot.services.repository.base_repository import BaseRepo

logger = logging.getLogger(__name__)


class GameRepo(BaseRepo):
    async def add_game_history_entry(self, game_history: models.GameHistoryEntry):
        self.session.add(game_history)

    async def update_game_score(self, game_id: UUID, new_score: int) -> None:
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
        query = (
            select(models.GameHistoryEntry)
            .filter_by(telegram_id=user_id)
            .order_by(models.GameHistoryEntry.score.desc())
            .limit(5)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def users_count(self) -> Optional[int]:
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
        query = (
            select(models.GameHistoryEntry)
            .filter_by(**filters)
            .order_by(models.GameHistoryEntry.score.desc())
            .limit(9)
        )
        result = await self.session.execute(query)
        return result.scalars().all()
