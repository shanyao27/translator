# контекстные проверки + таблица символов
from __future__ import annotations
from typing import Dict
from src.ast.ast_nodes import *
from src.errors import SemanticError

NUMERIC = {"integer", "real"}
BOOL = {"boolean"}
CHAR = {"char"}
STRING = {"string"}

class SemanticChecker:
    def __init__(self):
        self.sym: Dict[str, str] = {}  # name -> type

    def check(self, prog: Program):
        # собрать объявления
        for d in prog.decls:
            for name in d.names:
                if name in self.sym:
                    raise SemanticError(4, f"Повторное объявление {name}")
                self.sym[name] = d.typ

        # пройтись по телу
        self.check_block(prog.body)

    def check_block(self, block: Block):
        for s in block.statements:
            self.check_stmt(s)

    def check_stmt(self, s: Stmt):
        if isinstance(s, Block):
            self.check_block(s)
        elif isinstance(s, Assign):
            if s.target not in self.sym:
                raise SemanticError(6, f"Идентификатор {s.target} не объявлен")
            t_left = self.sym[s.target]
            t_right = self.check_expr(s.expr)
            if not self.assignable(t_left, t_right):
                raise SemanticError(7, f"Несовместимые типы в присваивании {t_left} := {t_right}")
        elif isinstance(s, If):
            t = self.check_expr(s.cond)
            if t != "boolean":
                raise SemanticError(11, "Условие if должно быть boolean")
            self.check_stmt(s.then_branch)
            if s.else_branch:
                self.check_stmt(s.else_branch)
        elif isinstance(s, While):
            t = self.check_expr(s.cond)
            if t != "boolean":
                raise SemanticError(11, "Условие while должно быть boolean")
            self.check_stmt(s.body)
        elif isinstance(s, For):
            if s.var not in self.sym:
                raise SemanticError(6, f"Идентификатор {s.var} не объявлен")
            if self.sym[s.var] not in NUMERIC:
                raise SemanticError(11, "Переменная for должна быть числовой")
            if self.check_expr(s.start) not in NUMERIC or self.check_expr(s.end) not in NUMERIC:
                raise SemanticError(11, "Границы for должны быть числовыми")
            self.check_stmt(s.body)
        elif isinstance(s, Repeat):
            for st in s.body:
                self.check_stmt(st)
            t = self.check_expr(s.until_cond)
            if t != "boolean":
                raise SemanticError(11, "Условие until должно быть boolean")
        elif isinstance(s, Writeln):
            for a in s.args:
                self.check_expr(a)
        elif isinstance(s, Readln):
            for name in s.args:
                if name not in self.sym:
                    raise SemanticError(6, f"Идентификатор {name} не объявлен")
        elif isinstance(s, Call):
            # для курсовой хватит проверки аргументов как выражений
            for a in s.args:
                self.check_expr(a)
        else:
            raise SemanticError(7, "Неизвестный оператор")

    def check_expr(self, e: Expr) -> str:
        if isinstance(e, Literal):
            return e.lit_type
        if isinstance(e, Identifier):
            if e.name not in self.sym:
                raise SemanticError(6, f"Идентификатор {e.name} не объявлен")
            return self.sym[e.name]
        if isinstance(e, UnaryOp):
            t = self.check_expr(e.operand)
            if e.op == "not":
                if t != "boolean":
                    raise SemanticError(7, "not применим только к boolean")
                return "boolean"
            if e.op == "-":
                if t not in NUMERIC:
                    raise SemanticError(7, "Унарный минус только для чисел")
                return t
            raise SemanticError(10, f"Неизвестный унарный оператор {e.op}")
        if isinstance(e, BinaryOp):
            tl = self.check_expr(e.left)
            tr = self.check_expr(e.right)
            op = e.op

            if op in {"+", "-", "*", "/", "mod"}:
                if tl not in NUMERIC or tr not in NUMERIC:
                    raise SemanticError(7, "Арифметика только над числами")
                if tl == "real" or tr == "real":
                    return "real"
                return "integer"

            if op in {"and", "or"}:
                if tl != "boolean" or tr != "boolean":
                    raise SemanticError(7, "Логические операции только над boolean")
                return "boolean"

            if op in {"=", "<>", "<", ">", "<=", ">="}:
                # сравнение чисел или одинаковых типов
                if (tl in NUMERIC and tr in NUMERIC) or (tl == tr):
                    return "boolean"
                raise SemanticError(7, "Несовместимые типы в сравнении")

            raise SemanticError(10, f"Неизвестный оператор {op}")

        if isinstance(e, Call):
            # пока считаем, что функция возвращает real если найдена, иначе integer
            for a in e.args:
                self.check_expr(a)
            return "real"
        raise SemanticError(7, "Неизвестное выражение")

    def assignable(self, left: str, right: str) -> bool:
        if left == right:
            return True
        if left == "real" and right == "integer":  # расширение
            return True
        return False
