from statistics import mean, stdev


def standartize(
    cols: list[list[float]],
    /,
    means: list[float] | None = None,
    stds: list[float] | None = None,
) -> list[list[float]]:
    if means is None:
        means = [mean(col) for col in cols]

    if stds is None:
        stds = [stdev(col) for col in cols]

    return [[((el - m) / s) for el in col] for col, m, s in zip(cols, means, stds)]


__all__ = [
    "standartize",
]
