from aiogram import Dispatcher, html, types
from aiogram.dispatcher.filters import (Command, CommandObject,
                                        ContentTypesFilter)

from bot.keyboards.game import GAME_SIZES
from bot.services.repository import GameRepo, SQLAlchemyRepos


async def stats(message: types.Message, repo: SQLAlchemyRepos):

    top_scores = await repo.get_repo(GameRepo).user_top_scores(
        user_id=message.from_user.id
    )

    if top_scores:
        text = "\n".join(
            [
                f"{i+1} | {g.field_size}X{g.field_size} | {g.played_at.date()} | {g.score}"
                for i, g in enumerate(top_scores)
            ]
        )
        await message.answer(html.pre(text), parse_mode="HTML")


async def stats_all(
    message: types.Message, repo: SQLAlchemyRepos, command: CommandObject
):
    game_size = None
    if command.args:
        if command.args[0] in map(str, GAME_SIZES):
            game_size = int(command.args[0])

    filters = {} if not game_size else {"field_size": game_size}
    all_users_top_scores = await repo.get_repo(GameRepo).all_users_top_scores(
        filters=filters
    )
    players = await repo.get_repo(GameRepo).users_count()

    if all_users_top_scores:
        top_games = []
        for i, game in enumerate(all_users_top_scores):
            user = "You" if game.telegram_id == message.from_user.id else "---"
            fields = [
                i + 1,
                user,
                f"{game.field_size}X{game.field_size}",
                game.played_at.date(),
                game.score,
            ]
            top_games.append(" | ".join(map(str, fields)))

        text = f"Players: {players}\n\n" + "\n".join(top_games)
        await message.answer(html.pre(text), parse_mode="HTML")


def register_stats(dp: Dispatcher):
    dp.message.register(
        stats,
        ContentTypesFilter(content_types="text"),
        Command(commands=("stats",)),
        flags={"throttling_key": "stats", "throttling_rate": 2},
    )
    dp.message.register(
        stats_all,
        ContentTypesFilter(content_types="text"),
        Command(commands=("stats_all",)),
        flags={"throttling_key": "stats", "throttling_rate": 2},
    )
