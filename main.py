import sys
from dataclasses import dataclass

from src import DataMatrix, Data, parse_vectors_file


@dataclass
class Args:
    data_file: str
    log_file: str


def parse_args(argv: list[str]) -> Args:
    args = Args(None)

    for i, arg in enumerate(argv):
        if arg == "-f" and i + 1 < len(argv):
            args.data_file = argv[i + 1]

    return args


def print_help() -> None:
    print("-f [filename]")


def main(args: Args):
    if not args.data_file:
        # TODO -- LOGGER
        print_help()
        return

    data = Data(DataMatrix(parse_vectors_file(args.f_name)))
    print(f"({data.dimensions}:{data.vector_length})")
    print(data.mean_vector)


if __name__ == "__main__":
    argv = sys.argv
    main(parse_args(argv))
