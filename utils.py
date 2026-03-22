from dataclasses import dataclass


@dataclass
class Args:
    data_file: str | None = None
    log_file: str | None = None


def print_help() -> None:
    print("-f [filename]")


def parse_args(argv: list[str]) -> Args:
    args = Args()

    for i, arg in enumerate(argv):
        if arg == "-h":
            print_help()
            exit(0)

        if arg == "-t":
            args.data_file = "data\\norm3n.txt"

        if (arg == "-f") and ((i + 1) < len(argv)):
            args.data_file = argv[i + 1]

    return args


def format_number(number) -> str:
    return f"{number:10.2f}"


def print_vector(vector) -> None:
    for x in vector:
        print(f"{format_number(x)}", end=" ")

    print()


def print_matrix(matrix) -> None:
    for row in matrix:
        print_vector(row)
