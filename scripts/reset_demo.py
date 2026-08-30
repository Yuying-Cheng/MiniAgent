from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


DEMO_SOURCE = """def add(a, b):
    return a - b


def multiply(a, b):
    return a * b

"""


def main() -> int:
    calculator = ROOT / "demo" / "calculator.py"
    calculator.write_text(DEMO_SOURCE, encoding="utf-8", newline="\n")
    print(f"Reset demo file: {calculator}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
