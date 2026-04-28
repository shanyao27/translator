import sys
from src.preprocessor import preprocess
from src.lexer.lexer import Lexer
from src.parser.parser import Parser
from src.semantic.semantic import SemanticChecker
from src.codegen.codegen_cpp import CppGenerator
from src.errors import TranslatorError
from src.file_validator import validate_file, read_file


def run(pas_text: str) -> str:
    cleaned = preprocess(pas_text)
    tokens = Lexer(cleaned).tokenize()
    prog = Parser(tokens).parse_program()
    SemanticChecker().check(prog)
    cpp = CppGenerator().gen(prog)
    return cpp


def run_file(path: str) -> str:
    pas_text = read_file(path)
    return run(pas_text)