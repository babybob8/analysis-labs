import sys
from src import Data, DataMatrix, parse_vectors_file
from utils import *


def main(args: Args):
    if not args.data_file:
        # TODO LOGGER (there will be UI so its kinda staying here until there is UI)
        print_help()
        return

    data = Data(args.data_file)
    print("Dim: ")
    print(f"{auto_format(data.dimensions)}")
    print("\nData len: ")
    print(f"{auto_format(data.vector_length)}")
    print("\nMean vector: ")
    print_vector(data.mean_vector)
    print("\nStddev vector: ")
    print_vector(data.std_vector)
    print("\nCorr matrix: ")
    print_matrix(data.correlation_matrix)
    print("\nCov matrix: ")
    print_matrix(data.covariance_matrix)
    print("\nPartial corr vector: ")
    print_vector(data.partial_correlation_vector)
    print("\nPartial corr significance vector: ")
    print_vector(data.partial_correlation_significance_vector)
    print("\nPartial corr significance intervals: ")
    for interval in data.partial_correlation_significance_intervals_vector:
        print_vector(interval)
    print("\nMultcorr vector: ")
    print_vector(data.mult_correlation_vector)


if __name__ == "__main__":
    argv = sys.argv
    main(parse_args(argv))
