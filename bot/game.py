import random
from enum import Enum, auto
from typing import List, Tuple
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, root_validator, validator

NEW_FIELD_MIN = 2
NEW_FIELD_MAX = 4
NEW_FIELD_MIN_CHANCE = 0.9

DEFAULT_FIELD_SIZE = 4


class Direction(Enum):
    LEFT = auto()
    UP = auto()
    RIGHT = auto()
    DOWN = auto()


class GameException(Exception):
    pass


class FieldNotModified(GameException):
    """Game field not modified"""


class Game(BaseModel):
    game_id: UUID = Field(default_factory=uuid4)
    size: int = DEFAULT_FIELD_SIZE
    score: int = 0
    field: List[List[int]] = None

    @validator("field", pre=True, always=True)
    def default_field(cls, v, *, values, **kwargs):
        size = values["size"]
        return v or [[0] * size for _ in range(size)]

    @root_validator
    def check_field_size_match(cls, values):
        size, field = values.get("size"), values.get("field")
        if size != len(field):
            raise ValueError("field doesnt match size")
        return values

    def start_game(self, fill_cells: int = 2):
        for _ in range(fill_cells):
            self._new_cell()

    @property
    def empty_cells(self) -> List[Tuple[int, int]]:
        """Return List[(y, x)] coordinates of empty cells"""

        empty = []
        for i_y, y in enumerate(self.field):
            for i_x, x in enumerate(y):
                if x == 0:
                    empty.append((i_y, i_x))
        return empty

    @property
    def game_over(self) -> bool:
        """Game over status, if game can`t be continued return True, otherwise False"""

        if not self.empty_cells:
            rotated_field = [list(row) for row in zip(*reversed(self.field))]
            for field in (self.field, rotated_field):
                for i_y, y in enumerate(field):
                    for i_x, x in enumerate(y):
                        if i_x < self.size - 1 and x == field[i_y][i_x + 1]:
                            return False
            return True
        else:
            return False

    def _new_cell(self):
        """Create new cell, if cell can`t be created raise FieldNotModified"""

        empty = self.empty_cells
        if not empty:
            raise FieldNotModified("There is no empty cells for new value")

        value = (
            NEW_FIELD_MAX if random.random() >= NEW_FIELD_MIN_CHANCE else NEW_FIELD_MIN
        )
        cell = random.choice(empty)
        self.field[cell[0]][cell[1]] = value

    def _shift(self):
        """Shift non-zero values to left border"""

        for i_row, row in enumerate(self.field):
            row = [i for i in row if i != 0]
            row.extend([0] * (self.size - len(row)))
            self.field[i_row] = row

    def _merge(self):
        """Merge equal neighbor values"""

        for i_y, y in enumerate(self.field):
            for i_x, x in enumerate(y):
                if x == 0:
                    continue
                if i_x < self.size - 1 and x == self.field[i_y][i_x + 1]:
                    self.field[i_y][i_x] = score = self.field[i_y][i_x] * 2
                    self.field[i_y][i_x + 1] = 0
                    self.score += score

            self._shift()

    def _rotate(self):
        """Rotate game field by 90 degrees"""

        self.field = [list(row) for row in zip(*reversed(self.field))]

    def _left(self):
        self._shift()
        self._merge()

    def _up(self):
        self._rotate()
        self._rotate()
        self._rotate()
        self._shift()
        self._merge()
        self._rotate()

    def _right(self):
        self._rotate()
        self._rotate()
        self._shift()
        self._merge()
        self._rotate()
        self._rotate()

    def _down(self):
        self._rotate()
        self._shift()
        self._merge()
        self._rotate()
        self._rotate()
        self._rotate()

    def move(self, direction: Direction):
        field_copy = self.field.copy()

        if direction is Direction.LEFT:
            self._left()
        elif direction is Direction.UP:
            self._up()
        elif direction is Direction.RIGHT:
            self._right()
        else:
            self._down()

        if field_copy != self.field:
            self._new_cell()
        else:
            raise FieldNotModified
