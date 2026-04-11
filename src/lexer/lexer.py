from __future__ import annotations
from dataclasses import dataclass
from typing import List
from src.tokens import Token, TokType, KEYWORDS, MULTI_OPS, SINGLE_OPS, DELIMS
from src.errors import LexError


@dataclass
class Lexer:
    text: str
    pos: int = 0
    line: int = 1
    col: int = 1

    def _peek(self, k=0):
        i = self.pos + k
        return self.text[i] if i < len(self.text) else "\0"

    def _advance(self):
        ch = self._peek()
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def _skip_ws(self):
        while self._peek().isspace():
            self._advance()

    def tokenize(self) -> List[Token]:
        tokens = []

        while True:
            self._skip_ws()
            ch = self._peek()
            if ch == "\0":
                tokens.append(Token(TokType.EOF, "EOF", self.line, self.col))
                return tokens

            start_line, start_col = self.line, self.col

            if ch.isalpha():
                buf = []
                while self._peek().isalnum() or self._peek() == "_":
                    buf.append(self._advance())
                word = "".join(buf).lower()

                if word in KEYWORDS:
                    if word in {"true", "false"}:
                        tokens.append(Token(TokType.BOOL, word, start_line, start_col))
                    else:
                        tokens.append(Token(TokType.KEYWORD, word, start_line, start_col))
                else:
                    tokens.append(Token(TokType.IDENT, word, start_line, start_col))
                continue

            if ch.isdigit():
                buf = []
                while self._peek().isdigit():
                    buf.append(self._advance())

                if self._peek() == "." and self._peek(1).isdigit():
                    buf.append(self._advance())
                    while self._peek().isdigit():
                        buf.append(self._advance())
                    tokens.append(Token(TokType.REAL, "".join(buf), start_line, start_col))
                else:
                    tokens.append(Token(TokType.INT, "".join(buf), start_line, start_col))
                continue

            if ch == "'":
                self._advance()
                buf = []
                while self._peek() not in {"'", "\0", "\n"}:
                    buf.append(self._advance())
                if self._peek() != "'":
                    raise LexError(9, "Missing closing quote", start_line, start_col)
                self._advance()
                s = "".join(buf)
                if len(s) == 1:
                    tokens.append(Token(TokType.CHAR, s, start_line, start_col))
                else:
                    tokens.append(Token(TokType.STRING, s, start_line, start_col))
                continue

            two = ch + self._peek(1)
            if two in MULTI_OPS:
                self._advance(); self._advance()
                tokens.append(Token(TokType.OP, two, start_line, start_col))
                continue

            if ch in SINGLE_OPS:
                self._advance()
                tokens.append(Token(TokType.OP, ch, start_line, start_col))
                continue

            if ch in DELIMS:
                self._advance()
                tokens.append(Token(TokType.DELIM, ch, start_line, start_col))
                continue

            raise LexError(10, f"Unknown symbol: {ch}", start_line, start_col)
