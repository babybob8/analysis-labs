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
            import sys

            args.data_file = (
                r".\data\norm3n.txt"
                if sys.platform == "win32"
                else r"./data/norm3n.txt"
            )

        if (arg == "-f") and ((i + 1) < len(argv)):
            args.data_file = argv[i + 1]

    return args


def auto_format(obj):
    if isinstance(obj, bool):
        return f"      True" if obj else "     False"

    elif isinstance(obj, float):
        return f"{obj:10.2f}"

    elif isinstance(obj, int):
        return f"{obj:10}"

    else:
        return obj


def print_vector(vector) -> None:
    for x in vector:
        print(f"{auto_format(x)}", end=" ")

    print()


def print_matrix(matrix) -> None:
    for row in matrix:
        print_vector(row)
