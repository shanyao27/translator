import sys
from src.preprocessor import preprocess
from src.lexer.lexer import Lexer
from src.parser.parser import Parser
from src.semantic.semantic import SemanticChecker
from src.codegen.codegen_cpp import CppGenerator
from src.errors import TranslatorError


def run(pas_text: str) -> str:
    cleaned = preprocess(pas_text)
    tokens = Lexer(cleaned).tokenize()
    prog = Parser(tokens).parse_program()
    SemanticChecker().check(prog)
    cpp = CppGenerator().gen(prog)
    return cpp
