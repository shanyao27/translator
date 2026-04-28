# все типы токенов, ключевые слова, операторы, разделители
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

# Ключевики Pascal из отчета
KEYWORDS = {
    "program", "const", "var", "begin", "end",
    "if", "then", "else",
    "while", "do",
    "for", "to", "downto",
    "repeat", "until",
    "writeln", "readln",
    "procedure", "function",
    "integer", "real", "char", "boolean",
    "true", "false",
    "and", "or", "not",
    "mod",
}

TYPE_KEYWORDS = {"integer", "real", "char", "boolean"}

# Операторы/разделители по грамматике
MULTI_OPS = {":=", "<=", ">=", "<>"}
SINGLE_OPS = {"+", "-", "*", "/", "=", "<", ">", "%"}  # % не в паскале, но оставлю на всякий
DELIMS = {";", ".", ",", "(", ")", ":"}
