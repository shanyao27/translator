from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto


class TokType(Enum):
    IDENT = auto()
    INT = auto()
    REAL = auto()
    CHAR = auto()
    STRING = auto()
    BOOL = auto()

    KEYWORD = auto()
    OP = auto()
    DELIM = auto()
    EOF = auto()


@dataclass(frozen=True)
class Token:
    type: TokType
    value: str
    line: int
    col: int


KEYWORDS = {
    "program", "var",
    "begin", "end",
    "if", "then", "else",
    "while", "do",
    "for", "to", "downto",
    "repeat", "until",
    "writeln", "readln",
    "procedure", "function",

    # типы
    "integer", "real", "char", "boolean", "string",

    # литералы
    "true", "false",

    # логика
    "and", "or", "not",

    # массивы
    "array", "of",

    # арифметика
    "mod",

    # новое
    "const", "type", "record", "case",
}

TYPE_KEYWORDS = {"integer", "real", "char", "boolean", "string"}


# Операторы
MULTI_OPS = {"<=", ">=", "<>", ":=", ".."}
SINGLE_OPS = {"+", "-", "*", "/", "=", "<", ">", "%"}

# Разделители
DELIMS = {";", ".", ",", "(", ")", "[", "]", ":"}
