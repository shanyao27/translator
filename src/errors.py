class TranslatorError(Exception):
    def __init__(self, code: int, msg: str, line: int | None = None, col: int | None = None):
        self.code = code
        self.msg = msg
        self.line = line
        self.col = col
        super().__init__(self.__str__())

    def __str__(self):
        pos = ""
        if self.line is not None and self.col is not None:
            pos = f" (line {self.line}, col {self.col})"
        return f"[Error {self.code}] {self.msg}{pos}"

class LexError(TranslatorError): ...
class ParseError(TranslatorError): ...
class SemanticError(TranslatorError): ...
class FileError(TranslatorError): ...