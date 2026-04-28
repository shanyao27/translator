import os
import pytest
import tempfile
from src.file_validator import validate_file, read_file
from src.errors import FileError


def make_file(name: str, content: str = "program Test; begin end.") -> str:
    path = os.path.join(tempfile.gettempdir(), name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def make_empty_file(name: str) -> str:
    path = os.path.join(tempfile.gettempdir(), name)
    open(path, "w").close()
    return path


def test_01_valid_file():
    path = make_file("valid.pas")
    validate_file(path)


def test_02_wrong_extension():
    path = make_file("file.txt")
    with pytest.raises(FileError, match="неверным расширением"):
        validate_file(path)


def test_03_empty_file():
    path = make_empty_file("empty.pas")
    with pytest.raises(FileError, match="пустой файл"):
        validate_file(path)


def test_04_forbidden_char_colon():
    with pytest.raises(FileError, match="недопустимые символы"):
        validate_file("fi:le.pas")


def test_05_space_in_name():
    path = make_file("my file.pas")
    with pytest.raises(FileError, match="недопустимые символы"):
        validate_file(path)


def test_06_name_too_long():
    long_name = "a" * 256 + ".pas"
    with pytest.raises(FileError, match="недопустимая длина"):
        validate_file(long_name)


def test_07_file_not_found():
    with pytest.raises(FileError, match="файл не выбран"):
        validate_file("nonexistent.pas")


def test_08_read_file_returns_content():
    path = make_file("readable.pas", "program Test; begin end.")
    content = read_file(path)
    assert "program" in content


def test_09_forbidden_char_question():
    with pytest.raises(FileError, match="недопустимые символы"):
        validate_file("fi?le.pas")


def test_10_forbidden_char_star():
    with pytest.raises(FileError, match="недопустимые символы"):
        validate_file("fi*le.pas")


def test_11_forbidden_char_pipe():
    with pytest.raises(FileError, match="недопустимые символы"):
        validate_file("fi|le.pas")


def test_12_forbidden_char_lt():
    with pytest.raises(FileError, match="недопустимые символы"):
        validate_file("fi<le.pas")


def test_13_forbidden_char_gt():
    with pytest.raises(FileError, match="недопустимые символы"):
        validate_file("fi>le.pas")


def test_14_name_exactly_255_chars():
    name = "a" * 255 + ".pas"
    with pytest.raises(FileError, match="файл не выбран"):
        validate_file(name)


def test_15_tab_in_name():
    with pytest.raises(FileError, match="недопустимые символы"):
        validate_file("my\tfile.pas")