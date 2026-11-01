import os
import subprocess
import sys

designer_path_win = r"./.venv/Lib/site-packages/PySide6/designer.exe"
designer_path_posix = r"./.venv/lib64/python3.14/site-packages/PySide6/designer"
uic_path_win = r"./.venv/Scripts/pyuic6.exe"
uic_path_posix = r"./.venv/bin/pyuic6"
dotui_path = r"./src/dotui/"
compui_path = r"./src/compui/"


def designer_run(designer_path: str):
    if not os.path.exists(designer_path):
        print(f"Couldn't find designer in({designer_path})")
        return

    print(f"Starting designer from({designer_path})")
    return subprocess.run(
        ["uv", "run", designer_path], capture_output=True, text=True, check=False
    )


def compile_ui(uic_path: str, from_path: str, to_path: str):
    if not os.path.exists(uic_path):
        print(f"Couldn't find uic in({uic_path})")
        return

    print(f"Compiling ui from({from_path}) to({to_path})")
    return subprocess.run(
        [
            "uv",
            "run",
            uic_path,
            "-w",
            "52",
            "-o",
            to_path,
            from_path,
        ],
        capture_output=True,
        text=True,
        check=False,
    )


if __name__ == "__main__":
    if sys.platform == "win32":
        res = designer_run(designer_path_win)
        if res is None:
            sys.exit(1)
        print(res.stdout)

        comp = compile_ui(uic_path_win, dotui_path, compui_path)
        if comp is None:
            sys.exit(1)
        print(comp.stdout)

    else:
        res = designer_run(designer_path_posix)
        if res is None:
            sys.exit(1)
        print(res.stdout)

        comp = compile_ui(uic_path_posix, dotui_path, compui_path)
        if comp is None:
            sys.exit(1)
        print(comp.stdout)
