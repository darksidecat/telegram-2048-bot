import json
from datetime import datetime
from typing import Optional
from uuid import UUID

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Command, ContentTypesFilter
from aiogram.dispatcher.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot import keyboards
from bot.db import GameHistoryEntry
from bot.game import Direction, FieldNotModified, Game
from bot.keyboards.game import GameAction, GameCD, GameSizeCD
from bot.utils import draw_table


def render_field(game: Game):
    return f"<code>{draw_table(game.field)}\n\nscore: {game.score}</code>"


async def start(message: types.Message):
    await message.answer(
        "Please select game field size", reply_markup=keyboards.game.game_size()
    )


async def new_game(
    query: types.CallbackQuery,
    state: FSMContext,
    callback_data: GameSizeCD,
    session: AsyncSession,
):
    game = Game(size=callback_data.size)
    game.start_game()

    await query.message.edit_text(
        text=render_field(game),
        reply_markup=keyboards.game.game_buttons(game.game_id),
        parse_mode="HTML",
    )

    await state.update_data(game=game.json())

    async with session.begin():
        game_history = GameHistoryEntry(
            game_id=game.game_id,
            played_at=datetime.utcnow(),
            telegram_id=query.from_user.id,
            field_size=game.size,
            score=0,
        )
        session.add(game_history)


async def move(
    query: types.CallbackQuery,
    state: FSMContext,
    callback_data: GameCD,
    session: AsyncSession,
):
    user_data = await state.get_data()
    game_data = user_data.get("game")

    if not game_data or callback_data.game_id != UUID(
        json.loads(game_data).get("game_id")
    ):
        await query.message.edit_text("This game is no longer available")
        await query.answer("This game is no longer available", show_alert=True)
        return

    game: Game = Game.parse_raw(game_data)

    if game.game_over:
        await query.message.edit_text(
            text="\n\n".join((render_field(game), "GameOver")),
            reply_markup=None,
            parse_mode="HTML",
        )
        return

    try:
        if callback_data.action == GameAction.LEFT:
            game.move(Direction.LEFT)
        elif callback_data.action == GameAction.UP:
            game.move(Direction.UP)
        elif callback_data.action == GameAction.RIGHT:
            game.move(Direction.RIGHT)
        elif callback_data.action == GameAction.DOWN:
            game.move(Direction.DOWN)
        else:
            await query.answer(cache_time=3)
            return
    except FieldNotModified:
        await query.answer()
        return

    await query.message.edit_text(
        text=render_field(game),
        reply_markup=keyboards.game.game_buttons(game.game_id),
        parse_mode="HTML",
    )

    await state.update_data(game=game.json())
    await query.answer()

    async with session.begin():
        game_history: Optional[GameHistoryEntry] = await session.get(
            GameHistoryEntry, game.game_id
        )
        if game_history:
            game_history.score = game.score


def register_game(dp: Dispatcher):
    dp.message.register(
        start,
        ContentTypesFilter(content_types="text"),
        Command(
            commands={
                "start",
            }
        ),
    )

    dp.callback_query.register(new_game, GameSizeCD.filter())

    dp.callback_query.register(move, GameCD.filter())
