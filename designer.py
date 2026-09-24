import sys, subprocess


if __name__ == "__main__":
    if sys.platform == "win32":
        res = subprocess.run(
            ["uv", "run", "./.venv/Lib/site-packages/PySide6/designer.exe"],
            capture_output=True,
            text=True,
        )
        print(res.stdout)
        comp = subprocess.run(
            [
                "uv",
                "run",
                "./.venv/Scripts/pyuic6.exe",
                "-w",
                "52",
                "-o",
                "./src/compui/",
                "./src/dotui/",
            ],
            capture_output=True,
            text=True,
        )
        print(comp.stdout)

    else:
        res = subprocess.run(
            ["uv", "run", "./.venv/lib64/python3.14/site-packages/PySide6/designer"],
            capture_output=True,
            text=True,
        )
        print(res.stdout)
        comp = subprocess.run(
            [
                "uv",
                "run",
                "./.venv/bin/pyuic6",
                "-w",
                "52",
                "-o",
                "./src/compui/",
                "./src/dotui/",
            ],
            capture_output=True,
            text=True,
        )
        print(comp.stdout)
