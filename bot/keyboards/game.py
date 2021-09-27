from enum import Enum
from uuid import UUID

from aiogram.dispatcher.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import KeyboardBuilder


class GameAction(str, Enum):
    PASS = "PASS"
    LEFT = "LEFT"
    UP = "UP"
    RIGHT = "RIGHT"
    DOWN = "DOWN"


class GameCD(CallbackData, prefix="game"):
    game_id: UUID
    action: GameAction


def game_buttons(game_id: UUID):
    empty_button = InlineKeyboardButton(
        text="‎", callback_data=GameCD(game_id=game_id, action=GameAction.PASS).pack()
    )
    left = InlineKeyboardButton(
        text="⬅️", callback_data=GameCD(game_id=game_id, action=GameAction.LEFT).pack()
    )
    up = InlineKeyboardButton(
        text="⬆️", callback_data=GameCD(game_id=game_id, action=GameAction.UP).pack()
    )
    right = InlineKeyboardButton(
        text="➡️", callback_data=GameCD(game_id=game_id, action=GameAction.RIGHT).pack()
    )
    down = InlineKeyboardButton(
        text="⬇️", callback_data=GameCD(game_id=game_id, action=GameAction.DOWN).pack()
    )

    keyboard = KeyboardBuilder(button_type=InlineKeyboardButton)
    keyboard.add(
        empty_button,
        up,
        empty_button,
        left,
        empty_button,
        right,
        empty_button,
        down,
        empty_button,
    )

    keyboard.adjust(3, repeat=True)

    return keyboard.as_markup()


class GameSizeCD(CallbackData, prefix="game_size"):
    size: int


def game_size():
    keyboard = KeyboardBuilder(button_type=InlineKeyboardButton)
    for i in range(4, 8):
        keyboard.add(
            InlineKeyboardButton(
                text=f"{i}X{i}", callback_data=GameSizeCD(size=i).pack()
            )
        )

    keyboard.adjust(2, repeat=True)

    return keyboard.as_markup()
