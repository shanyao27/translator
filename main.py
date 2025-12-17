import sys
from src.pipeline import run
from src.errors import TranslatorError


def main():
    if len(sys.argv) < 3:
        print("Usage: python main.py input.pas output.cpp")
        sys.exit(1)

    in_path, out_path = sys.argv[1], sys.argv[2]

    try:
        with open(in_path, "r", encoding="utf-8") as f:
            pas_text = f.read()

        cpp_code = run(pas_text)

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(cpp_code)

        print(f"Successfully written: {out_path}")

    except TranslatorError as err:
        print(err)
        sys.exit(1)


if __name__ == "__main__":
    main()