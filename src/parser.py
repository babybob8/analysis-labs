def parse_vectors_file(path: str) -> list[list[float]]:
    vectors: list[list[float]] = []

    with open(path, "r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, 1):
            stripped = line.strip()
            if not stripped:
                continue

            try:
                vector = [float(x) for x in stripped.split()]
            except ValueError as e:
                raise ValueError(f"Parsing error at: {line_number}: {stripped}") from e

            vectors.append(vector)

    return vectors
