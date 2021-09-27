import random
from typing import List
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator

NEW_FIELD_MIN = 2
NEW_FIELD_MAX = 4
NEW_FIELD_MIN_CHANCE = 0.9

DEFAULT_FIELD_SIZE = 4


class GameException(Exception):
    pass


class FieldNotModified(GameException):
    pass


class Game(BaseModel):
    game_id: UUID = Field(default_factory=uuid4)
    size: int = DEFAULT_FIELD_SIZE
    score: int = 0
    field: List[List[int]] = None

    @validator("field", pre=True, always=True)
    def default_field(cls, v, *, values, **kwargs):
        size = values["size"]
        return v or [[0] * size for _ in range(size)]

    def start_game(self, fill_cells: int = 2):
        for _ in range(fill_cells):
            self._new_cell()

    @property
    def empty_cells(self):
        empty = []
        for i_y, y in enumerate(self.field):
            for i_x, x in enumerate(y):
                if x == 0:
                    empty.append((i_y, i_x))
        return empty

    @property
    def game_over(self):
        if not self.empty_cells:
            for i_y, y in enumerate(self.field):
                for i_x, x in enumerate(y):
                    if i_x < self.size - 1 and x == self.field[i_y][i_x + 1]:
                        return False

            rotated_field = [list(row) for row in zip(*reversed(self.field))]
            for i_y, y in enumerate(rotated_field):
                for i_x, x in enumerate(y):
                    if i_x < self.size - 1 and x == rotated_field[i_y][i_x + 1]:
                        return False

            return True
        else:
            return False

    def _new_cell(self):
        empty = self.empty_cells

        value = (
            NEW_FIELD_MAX if random.random() >= NEW_FIELD_MIN_CHANCE else NEW_FIELD_MIN
        )
        cell = random.choice(empty)
        self.field[cell[0]][cell[1]] = value

    def _shift(self):
        for i_row, row in enumerate(self.field):
            row = [i for i in row if i != 0]
            row.extend([0] * (self.size - len(row)))
            self.field[i_row] = row

    def _merge(self):
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
        self.field = [list(row) for row in zip(*reversed(self.field))]

    def move_left(self):
        field_copy = self.field.copy()
        self._shift()
        self._merge()
        if field_copy != self.field:
            self._new_cell()
        else:
            raise FieldNotModified

    def move_up(self):
        field_copy = self.field.copy()
        self._rotate()
        self._rotate()
        self._rotate()
        self._shift()
        self._merge()
        self._rotate()
        if field_copy != self.field:
            self._new_cell()
        else:
            raise FieldNotModified

    def move_right(self):
        field_copy = self.field.copy()
        self._rotate()
        self._rotate()
        self._shift()
        self._merge()
        self._rotate()
        self._rotate()
        if field_copy != self.field:
            self._new_cell()
        else:
            raise FieldNotModified

    def move_down(self):
        field_copy = self.field.copy()

        self._rotate()
        self._shift()
        self._merge()
        self._rotate()
        self._rotate()
        self._rotate()

        if field_copy != self.field:
            self._new_cell()
        else:
            raise FieldNotModified
