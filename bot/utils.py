from typing import List


def draw_table(
    field: List[List[int]],
    min_cell_size=5,
    c_symbol="+",
    h_symbol="-",
    v_symbol="|",
    zero_placeholder=" ",
):
    table_size = len(field)
    min_cell_size = max(len(str(max(map(max, field)))), min_cell_size)

    text = ""
    for i, line in enumerate(field):
        if i == 0:
            text += (c_symbol + h_symbol * min_cell_size) * table_size + c_symbol + "\n"
        for value in line:
            text += v_symbol + str(zero_placeholder if value == 0 else value).center(
                min_cell_size
            )
        text += v_symbol + "\n"
        text += (c_symbol + h_symbol * min_cell_size) * table_size + c_symbol + "\n"

    return text
