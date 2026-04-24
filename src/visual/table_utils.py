from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem


matrix_t = list[list[float | int | bool | str]]
vector_t = list[float | int | bool | str]


def is_matrix(obj):
    return (
        isinstance(obj, list)
        and len(obj) > 0
        and all(isinstance(row, list) for row in obj)
    )


def is_vector(obj):
    return (
        isinstance(obj, list)
        and len(obj) > 0
        and all(not isinstance(x, list) for x in obj)
    )


def _format_float(item: float) -> str:
    return f"{item:.3f}"


def _format_bool(item: bool) -> str:
    return "True" if item else "False"


def _auto_format(item: float | int | bool | str) -> str:
    if isinstance(item, float):
        return _format_float(item)

    elif isinstance(item, bool):
        return _format_bool(item)

    elif isinstance(item, int):
        return _format_float(float(item))

    elif isinstance(item, str):
        return item

    else:
        return f"{item}"


def _fill_wmatrix(table: QTableWidget, matrix: matrix_t, dim: int, header: list[str] | None = None) -> None:
    table.clear()
    table.setRowCount(dim)
    table.setColumnCount(dim)
    
    if header is not None:
        table.setMaximumHeight(32 + (32 * dim))

        for i, vec in enumerate(matrix):
            table.setVerticalHeaderItem(i, QTableWidgetItem(header[i]))
            table.setHorizontalHeaderItem(i, QTableWidgetItem(header[i]))
            for j, val in enumerate(vec):
                table.setItem(i, j, QTableWidgetItem(_auto_format(val)))
    else:
        table.setMaximumHeight(32 * dim)

        for i, vec in enumerate(matrix):
            table.setVerticalHeaderItem(i, QTableWidgetItem())
            table.setHorizontalHeaderItem(i, QTableWidgetItem())
            for j, val in enumerate(vec):
                table.setItem(i, j, QTableWidgetItem(_auto_format(val)))
        

def _fill_wvector(
    table: QTableWidget, vector: vector_t, length: int, header: list[str] | None = None
) -> None:
    table.clear()
    table.setRowCount(1)
    table.setColumnCount(length)
    
    if header is not None:
        table.setMaximumHeight(64)
        for j in range(length):
            table.setHorizontalHeaderItem(j, QTableWidgetItem(header[j]))
            table.setItem(0, j, QTableWidgetItem(_auto_format(vector[j])))

    else:
        table.setMaximumHeight(32)
        table.setVerticalHeaderItem(0, QTableWidgetItem())
        for j, val in enumerate(vector):
            table.setHorizontalHeaderItem(j, QTableWidgetItem())
            table.setItem(0, j, QTableWidgetItem(_auto_format(val)))


def _fill_wsingle(table: QTableWidget, item: str) -> None:
    table.clear()
    table.setRowCount(1)
    table.setColumnCount(1)
    table.setMaximumHeight(31)
    table.setHorizontalHeaderItem(0, QTableWidgetItem())
    table.setVerticalHeaderItem(0, QTableWidgetItem())
    table.setItem(0, 0, QTableWidgetItem(item))


def fill_table(
    table: QTableWidget,
    filler: matrix_t | vector_t | float | int | bool | str,
    header: list[str] | None = None,
) -> None:
    if is_matrix(filler):
        dim = len(filler)
        if dim != len(filler[0]):
            raise ValueError("Matrix is not square.")

        _fill_wmatrix(table, filler, dim, header)

    elif is_vector(filler):
        length = len(filler)
        _fill_wvector(table, filler, length, header)

    elif isinstance(filler, float):
        formated = _auto_format(filler)
        _fill_wsingle(table, formated)

    elif isinstance(filler, bool):
        formated = _auto_format(filler)
        _fill_wsingle(table, formated)

    elif isinstance(filler, int):
        formated = _auto_format(float(filler))
        _fill_wsingle(table, formated)

    elif isinstance(filler, str):
        _fill_wsingle(table, filler)
