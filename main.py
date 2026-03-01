import sys
from dataclasses import dataclass
from src import DataMatrix, Data, parse_vectors_file


@dataclass
class Args:
    data_file: str | None = None
    log_file: str | None = None
    
def print_help() -> None:
    print("-f [filename]")

def parse_args(argv: list[str]) -> Args:
    args = Args()

    for i, arg in enumerate(argv):
        if (arg == "-h"):
            print_help()
            exit(0)
        
        if (arg == "-f") and ((i + 1) < len(argv)):
            args.data_file = argv[i + 1]

    return args

def print_matrix(matrix) -> None:
    for row in matrix:
        print(" ".join(f"{x:10.2f}" for x in row))
        
def main(args: Args):
    if not args.data_file:
        # TODO -- LOGGER
        print_help()
        return

    data = Data(DataMatrix(parse_vectors_file(args.data_file)))
    print(f"({data.dimensions}:{data.vector_length})")
    print(data.mean_vector)
    print()
    print_matrix(data.correlation_matrix)
    print()
    print_matrix(data.covariance_matrix)


if __name__ == "__main__":
    argv = sys.argv
    main(parse_args(argv))
