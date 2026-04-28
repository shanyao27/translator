from src.pipeline import run

def load(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def normalize(text: str) -> str:
    """Нормализует код, чтобы не падать из-за пробелов."""
    lines = [
        line.strip()
        for line in text.replace("\r", "").split("\n")
        if line.strip()
    ]
    return "\n".join(lines)


def test_hello_program():
    pas = load("examples/hello.pas")
    expected_cpp = load("examples/hello_expected.cpp")

    actual_cpp = run(pas)

    assert normalize(actual_cpp) == normalize(expected_cpp)