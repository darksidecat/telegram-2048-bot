import json
import logging
from datetime import datetime
from uuid import UUID

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Command, ContentTypesFilter
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.exceptions import TelegramRetryAfter

from bot import keyboards
from bot.db import GameHistoryEntry
from bot.game import Direction, FieldNotModified, Game
from bot.keyboards.game import GameAction, GameCD, GameSizeCD
from bot.services.repository import GameRepo, SQLAlchemyRepos
from bot.utils import draw_table

logger = logging.getLogger(__name__)


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
    repo: SQLAlchemyRepos,
):
    game = Game(size=callback_data.size)
    game.start_game()

    await query.message.edit_text(
        text=render_field(game),
        reply_markup=keyboards.game.game_buttons(game.game_id),
        parse_mode="HTML",
    )

    await state.update_data(game=game.json())

    await repo.get_repo(GameRepo).add_game_history_entry(
        GameHistoryEntry(
            game_id=game.game_id,
            played_at=datetime.utcnow(),
            telegram_id=query.from_user.id,
            field_size=game.size,
            score=0,
        ),
    )
    await repo.commit()


async def move(
    query: types.CallbackQuery,
    state: FSMContext,
    callback_data: GameCD,
    repo: SQLAlchemyRepos,
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

    try:
        await query.message.edit_text(
            text=render_field(game),
            reply_markup=keyboards.game.game_buttons(game.game_id),
            parse_mode="HTML",
        )
    except TelegramRetryAfter as err:
        """
        There is limits for editing messages in chat
        - small messages (<512 bytes) >200 edits in minute
        - bigger messages (>512 bytes) ~20 edits in minute

        4-5 game size is small messages, 6-7 is bigger messages
        """
        await query.message.answer(
            text=(
                f"Sorry, bot in Flood Control, please wait {err.retry_after} seconds or play 4-5 game sizes :(\n"
                f"Be careful, starting a new game will delete the progress in the old one"
            )
        )
        logger.warning(err)
        return

    await state.update_data(game=game.json())
    await query.answer()

    await repo.get_repo(GameRepo).update_game_score(
        game_id=game.game_id, new_score=game.score
    )
    await repo.commit()


def register_game(dp: Dispatcher):
    dp.message.register(
        start,
        ContentTypesFilter(content_types="text"),
        Command(commands=("start",)),
    )
    dp.callback_query.register(new_game, GameSizeCD.filter())
    dp.callback_query.register(move, GameCD.filter())
