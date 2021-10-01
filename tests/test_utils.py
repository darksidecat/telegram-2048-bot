import pytest

from bot import utils


@pytest.mark.parametrize(
    "field, result",
    [
        [
            [[1, 2], [3, 4]],
            """+-----+-----+
|  1  |  2  |
+-----+-----+
|  3  |  4  |
+-----+-----+
""",
        ],
        [
            [[12345, 2], [3, 4]],
            """+-----+-----+
|12345|  2  |
+-----+-----+
|  3  |  4  |
+-----+-----+
""",
        ],
        [
            [[123456, 2], [3, 4]],
            """+------+-----+
|123456|  2  |
+------+-----+
|  3   |  4  |
+------+-----+
""",
        ],
    ],
)
def test_draw_table(field, result):
    assert utils.draw_table(field) == result
