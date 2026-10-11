from .data import Data, DataMatrix


def filter_3sigma(data: Data) -> Data:
    new = [
        [data.cols[vec][val] for vec in range(data.dimensions)]
        for val in range(data.vector_length)
        if all(
            abs(data.cols[vec][val] - data.mean_vector[vec]) < 3 * data.std_vector[vec]
            for vec in range(data.dimensions)
        )
    ]
    
    return Data(DataMatrix(rows=new))
    