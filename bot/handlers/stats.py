from typing import List, Optional

from aiogram import Dispatcher, html, types
from aiogram.dispatcher.filters import Command, ContentTypesFilter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db import GameHistoryEntry


async def stats(message: types.Message, session: AsyncSession):

    async with session.begin():
        query = (
            select(GameHistoryEntry)
            .filter_by(telegram_id=message.from_user.id)
            .order_by(GameHistoryEntry.score.desc())
            .limit(5)
        )
        result = await session.execute(query)
        top_scores: Optional[List[GameHistoryEntry]] = result.scalars().all()

    if top_scores:
        text = "\n".join(
            [
                f"{i+1}: {g.field_size}X{g.field_size} - {g.played_at.date()}: {g.score}"
                for i, g in enumerate(top_scores)
            ]
        )
        await message.answer(html.pre(text), parse_mode="HTML")


def register_stats(dp: Dispatcher):
    dp.message.register(
        stats,
        ContentTypesFilter(content_types="text"),
        Command(
            commands={
                "stats",
            }
        ),
    )
