import os
from src.errors import FileError

FORBIDDEN_CHARS = set('/\\:*?"<>|')
MAX_NAME_LEN = 255


def validate_file(path: str) -> None:
    basename = os.path.basename(path)

    name, ext = os.path.splitext(basename)

    if ext.lower() != ".pas":
        raise FileError(1, "Ошибка: файл с неверным расширением")

    if not name:
        raise FileError(4, "Ошибка: имя файла содержит недопустимые символы")

    if len(name) > MAX_NAME_LEN:
        raise FileError(3, "Ошибка: недопустимая длина имени файла")

    if any(ch in FORBIDDEN_CHARS for ch in name):
        raise FileError(4, "Ошибка: имя файла содержит недопустимые символы")

    if any(ch.isspace() for ch in name):
        raise FileError(4, "Ошибка: имя файла содержит недопустимые символы")

    if not os.path.exists(path):
        raise FileError(5, "Ошибка: файл не выбран")

    if os.path.getsize(path) == 0:
        raise FileError(2, "Ошибка: пустой файл")


def read_file(path: str) -> str:
    validate_file(path)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()