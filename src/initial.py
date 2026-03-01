from statistics import mean


def mean_vector(parsed_data: list[list[float]]) -> list[float]:
    mean_vector = []
    for vector in parsed_data:
        mean_vector.append(mean(vector))

    return mean_vector
