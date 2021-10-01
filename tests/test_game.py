from unittest.mock import Mock, patch

import pytest
from pydantic import ValidationError

from bot.game import Direction, FieldNotModified, Game


class TestGame:
    def test_init(self):
        game = Game(size=4)
        assert len(game.field) == 4

    def test_init_field_doesnt_match_size(self):
        with pytest.raises(ValidationError):
            game = Game(size=3, field=[[1, 2], [3, 4]])

    def test_empty_cells(self):
        field = [
            [1, 1, 1],
            [1, 1, 0],
            [0, 1, 1],
        ]

        game = Game(size=3, field=field)
        assert game.empty_cells == [(1, 2), (2, 0)]

    @pytest.mark.parametrize(
        "field, result",
        [
            [[[1, 2], [3, 4]], True],
            [[[2, 1], [2, 4]], False],
        ],
    )
    def test_game_over(self, field, result):
        assert Game(field=field, size=len(field)).game_over == result

    def test_new_cell(self):
        game = Game(field=[[0, 1], [2, 3]], size=2)
        game._new_cell()
        assert game.field[0][0] != 0

    def test_new_cell_raise(self):
        game = Game(field=[[2, 1], [2, 3]], size=2)
        with pytest.raises(FieldNotModified):
            game._new_cell()

    def test_shift(self):
        game = Game(field=[[0, 1], [0, 2]], size=2)
        game._shift()
        assert game.field == [[1, 0], [2, 0]]

    def test_merge(self):
        game = Game(
            field=[
                [2, 0, 0, 2],
                [2, 2, 2, 0],
                [2, 2, 4, 4],
                [1, 2, 3, 4],
            ],
            size=4,
        )
        game._shift()
        game._merge()
        assert game.field == [
            [4, 0, 0, 0],
            [4, 2, 0, 0],
            [4, 8, 0, 0],
            [1, 2, 3, 4],
        ]

    def test_rotate(self):
        game = Game(field=[[1, 2], [3, 4]], size=2)
        game._rotate()
        assert game.field == [[3, 1], [4, 2]]

    @pytest.mark.parametrize(
        "field, direction, result",
        [
            [
                [[2, 2], [0, 4]],
                Direction.LEFT,
                [[4, 0], [4, 0]],
            ],
            [
                [[2, 2], [2, 4]],
                Direction.UP,
                [[4, 2], [0, 4]],
            ],
            [
                [[2, 2], [0, 4]],
                Direction.RIGHT,
                [[0, 4], [0, 4]],
            ],
            [
                [[2, 2], [2, 4]],
                Direction.DOWN,
                [[0, 2], [4, 4]],
            ],
        ],
    )
    def test_move(self, field, direction, result):
        with patch("bot.game.Game._new_cell", new_callable=Mock()):
            game = Game(field=field, size=len(field))
            game.move(direction)
            assert game.field == result
