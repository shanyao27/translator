from src.preprocessor import preprocess
from src.lexer.lexer import Lexer
from src.parser.parser import Parser
from src.semantic.semantic import SemanticChecker
from src.codegen.codegen_cpp import CppGenerator
from src.errors import TranslatorError

class Translator:
    def __init__(self, target_language="cpp"):
        self.target = target_language
        if target_language == "cpp":
            self.generator = CppGenerator()
        # Для других языков:
        # elif target_language == "python":
        #     self.generator = PythonGenerator()
    
    def translate(self, pas_text: str) -> str:
        cleaned = preprocess(pas_text)
        tokens = Lexer(cleaned).tokenize()
        prog = Parser(tokens).parse_program()
        checker = SemanticChecker()
        checker.check(prog)  # Теперь check вызывает accept
        return self.generator.gen(prog)

def run(pas_text: str) -> str:
    translator = Translator("cpp")
    return translator.translate(pas_text)