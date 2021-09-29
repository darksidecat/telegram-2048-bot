from typing import List, Optional

from aiogram import Dispatcher, html, types
from aiogram.dispatcher.filters import Command, ContentTypesFilter, CommandObject
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db import GameHistoryEntry
from bot.keyboards.game import GAME_SIZES


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
                f"{i+1} | {g.field_size}X{g.field_size} | {g.played_at.date()} | {g.score}"
                for i, g in enumerate(top_scores)
            ]
        )
        await message.answer(html.pre(text), parse_mode="HTML")


async def stats_all(message: types.Message, session: AsyncSession, command: CommandObject):
    game_size = None
    if command.args:
        if command.args[0] in GAME_SIZES:
            game_size = int(command.args[0])

    async with session.begin():
        query = (
            select(GameHistoryEntry)
            .filter(True if not game_size else (GameHistoryEntry.field_size == game_size))
            .order_by(GameHistoryEntry.score.desc())
            .limit(9)
        )
        result = await session.execute(query)
        top_scores: Optional[List[GameHistoryEntry]] = result.scalars().all()

        query = (
            select(func.count()).select_from(
                select(GameHistoryEntry)
                .distinct(GameHistoryEntry.telegram_id).subquery()
            )
        )
        result = await session.execute(query)
        players = result.scalar()

    if top_scores:
        top_games = []
        for i, game in enumerate(top_scores):
            user = 'You' if game.telegram_id == message.from_user.id else '---'
            fields = [i+1, user, f'{game.field_size}X{game.field_size}', game.played_at.date(), game.score]
            top_games.append(" | ".join(map(str, fields)))

        text = f"Players: {players}\n\n" + "\n".join(top_games)
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
    dp.message.register(
        stats_all,
        ContentTypesFilter(content_types="text"),
        Command(
            commands={
                "stats_all",
            }
        ),
    )
