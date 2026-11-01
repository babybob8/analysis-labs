import logging


def parse_vectors_file(path: str) -> list[list[float]]:
    vectors: list[list[float]] = []

    with open(path, "r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, 1):
            stripped = line.strip()
            if not stripped:
                continue

            try:
                vector = [float(x) for x in stripped.split()]
                vectors.append(vector)

            except ValueError:
                logging.error(f"Parsing error at: {line_number}: {stripped}")
                # raise ValueError() from e

    return vectors
