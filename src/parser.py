import logging
from typing import Optional

DELIMITERS = (";", "\t", ",")


def detect_delimiter(line: str) -> Optional[str]:
    return next((d for d in DELIMITERS if d in line), None)


def split_line(line: str, delimiter: Optional[str]) -> list[str]:
    tokens = line.split(delimiter) if delimiter else line.split()
    return [token.strip() for token in tokens]


def to_float(token: str, delimiter: Optional[str]) -> float:
    return float(token if delimiter == "," else token.replace(",", "."))


def is_numeric_row(tokens: list[str], delimiter: Optional[str]) -> bool:
    try:
        return all(isinstance(to_float(t, delimiter), float) for t in tokens)
    except ValueError:
        return False


def read_nonempty_lines(path: str) -> list[tuple[int, str]]:
    with open(path, "r", encoding="utf-8-sig") as f:
        return [
            (number, line.strip()) for number, line in enumerate(f, 1) if line.strip()
        ]


def parse_row(
    number: int, line: str, delimiter: Optional[str]
) -> Optional[list[float]]:
    try:
        return [to_float(t, delimiter) for t in split_line(line, delimiter)]
    except ValueError:
        logging.error("Parsing error at line %d: %s", number, line)
        return None


def parse_table_file(
    path: str,
) -> tuple[Optional[list[str]], list[list[float]]]:
    lines = read_nonempty_lines(path)
    if not lines:
        return None, []

    delimiter = detect_delimiter(lines[0][1])
    first_tokens = split_line(lines[0][1], delimiter)
    has_header = not is_numeric_row(first_tokens, delimiter)

    header = first_tokens if has_header else None
    body = lines[1:] if has_header else lines

    rows = [parse_row(number, line, delimiter) for number, line in body]
    return header, [row for row in rows if row is not None]


def parse_vectors_file(path: str) -> list[list[float]]:
    return parse_table_file(path)[1]
