from src.pipeline import run

def load(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def normalize(text: str) -> str:
    lines = [
        line.strip()
        for line in text.replace("\r", "").split("\n")
        if line.strip()
    ]
    return "\n".join(lines)


def test_hello_program():
    pas = load("tests/hello/hello.pas")
    expected = load("tests/hello/hello.cpp")

    actual_cpp = run(pas)

    assert normalize(actual_cpp) == normalize(expected)

def test_arithmetic():
    pas = load("tests/arithmetic/arithmetic.pas")
    expected = load("tests/arithmetic/arithmetic.cpp")

    actual_cpp = run(pas)

    assert normalize(actual_cpp) == normalize(expected)

def test_types():
    pas = load("tests/types/types.pas")
    expected = load("tests/types/types.cpp")

    actual_cpp = run(pas)

    assert normalize(actual_cpp) == normalize(expected)

def test_if_else():
    pas = load("tests/if_else/if_else.pas")
    expected = load("tests/if_else/if_else.cpp")

    actual_cpp = run(pas)

    assert normalize(actual_cpp) == normalize(expected)

def test_nested_if():
    pas = load("tests/nested_if/nested_if.pas")
    expected = load("tests/nested_if/nested_if.cpp")

    actual_cpp = run(pas)

    assert normalize(actual_cpp) == normalize(expected)

def test_while():
    pas = load("tests/while/while.pas")
    expected = load("tests/while/while.cpp")

    actual_cpp = run(pas)

    assert normalize(actual_cpp) == normalize(expected)

def test_repeat():
    pas = load("tests/repeat/repeat.pas")
    expected = load("tests/repeat/repeat.cpp")

    actual_cpp = run(pas)

    assert normalize(actual_cpp) == normalize(expected)

def test_for():
    pas = load("tests/for/for.pas")
    expected = load("tests/for/for.cpp")

    actual_cpp = run(pas)

    assert normalize(actual_cpp) == normalize(expected)

def test_nested_for():
    pas = load("tests/nested_for/nested_for.pas")
    expected = load("tests/nested_for/nested_for.cpp")

    actual_cpp = run(pas)

    assert normalize(actual_cpp) == normalize(expected)

def test_arrays():
    pas = load("tests/arrays/arrays.pas")
    expected = load("tests/arrays/arrays.cpp")

    actual_cpp = run(pas)

    assert normalize(actual_cpp) == normalize(expected)

def test_IfForWhileRepeat():
    pas = load("tests/IfForWhileRepeat/IfForWhileRepeat.pas")
    expected = load("tests/IfForWhileRepeat/IfForWhileRepeat.cpp")

    actual_cpp = run(pas)

    assert normalize(actual_cpp) == normalize(expected)

def test_funtion():
    pas = load("tests/function/function.pas")
    expected = load("tests/function/function.cpp")

    actual_cpp = run(pas)

    assert normalize(actual_cpp) == normalize(expected)

def test_strings():
    pas = load("tests/strings/strings.pas")
    expected = load("tests/strings/strings.cpp")

    actual_cpp = run(pas)

    assert normalize(actual_cpp) == normalize(expected)


def test_const():
    pas = load("tests/const/const.pas")
    expected = load("tests/const/const.cpp")

    actual_cpp = run(pas)

    assert normalize(actual_cpp) == normalize(expected)


def test_case():
    pas = load("tests/case/case.pas")
    expected = load("tests/case/case.cpp")

    actual_cpp = run(pas)

    assert normalize(actual_cpp) == normalize(expected)


def test_record():
    pas = load("tests/record/record.pas")
    expected = load("tests/record/record.cpp")

    actual_cpp = run(pas)

    assert normalize(actual_cpp) == normalize(expected)