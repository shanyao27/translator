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
        self.sym: Dict[str, Union[str, ArrayType]] = {}      # global vars + array types
        self.subs: Dict[str, SubroutineDecl] = {}            # procedures & functions
        self.current_function: str | None = None             # для return через fname := expr

    # =================================================================
    # MAIN ENTRY
    # =================================================================
    def check(self, prog: Program):
        # GLOBAL VARS
        for d in prog.decls:
            for name in d.names:
                if name in self.sym:
                    raise SemanticError(4, f"Повторное объявление {name}")
                self.sym[name] = d.typ

        # SUBROUTINES
        for sub in prog.subroutines:
            if sub.name in self.subs:
                raise SemanticError(4, f"Повторное объявление подпрограммы {sub.name}")
            self.subs[sub.name] = sub

        # CHECK SUBROUTINES FIRST
        for sub in prog.subroutines:
            self.check_subroutine(sub)

        # CHECK MAIN BLOCK
        self.check_block(prog.body)

    # =================================================================
    # SUBROUTINES
    # =================================================================
    def check_subroutine(self, sub: SubroutineDecl):

        # local symbol table
        local = {}

        # parameters
        for p in sub.params:
            if p.name in local:
                raise SemanticError(4, f"Повтор параметра {p.name}")
            local[p.name] = p.typ

        # handle functions
        saved = self.current_function
        if isinstance(sub, FunctionDecl):
            self.current_function = sub.name
            local[sub.name] = sub.ret_type

        # check body
        self.check_block(sub.body, local)

        self.current_function = saved

    # =================================================================
    # BLOCK CHECK
    # =================================================================
    def check_block(self, block: Block, local: Dict[str, str] | None = None):
        if local is None:
            local = {}

        for stmt in block.statements:
            self.check_stmt(stmt, local)

    # =================================================================
    # STATEMENT CHECK
    # =================================================================
    def check_stmt(self, s: Stmt, local):
        # BLOCK
        if isinstance(s, Block):
            self.check_block(s, local)
            return

        # ASSIGN
        if isinstance(s, Assign):

            # FUNCTION RETURN: fname := expr
            if isinstance(s.target, str) and s.target == self.current_function:
                t_right = self.check_expr(s.expr, local)
                t_expected = local[s.target]
                if not self.assignable(t_expected, t_right):
                    raise SemanticError(7, f"Тип возврата функции {self.current_function} должен быть {t_expected}")
                return

            # обычное присваивание
            t_left = self.resolve_var(s.target, local)
            t_right = self.check_expr(s.expr, local)
            if not self.assignable(t_left, t_right):
                raise SemanticError(7, f"Несовместимые типы: {t_left} := {t_right}")
            return

        # IF
        if isinstance(s, If):
            cond = self.check_expr(s.cond, local)
            if cond != "boolean":
                raise SemanticError(11, "Условие if должно быть boolean")
            self.check_stmt(s.then_branch, local)
            if s.else_branch:
                self.check_stmt(s.else_branch, local)
            return

        # WHILE
        if isinstance(s, While):
            cond = self.check_expr(s.cond, local)
            if cond != "boolean":
                raise SemanticError(11, "Условие while должно быть boolean")
            self.check_stmt(s.body, local)
            return

        # FOR
        if isinstance(s, For):
            if s.var not in self.sym and s.var not in local:
                raise SemanticError(6, f"Идентификатор {s.var} не объявлен")

            var_type = self.resolve_type(s.var, local)

            if var_type not in NUMERIC:
                raise SemanticError(11, "Переменная for должна быть числовой")

            t_start = self.check_expr(s.start, local)
            t_end = self.check_expr(s.end, local)

            if t_start not in NUMERIC or t_end not in NUMERIC:
                raise SemanticError(11, "Границы for должны быть числовыми")

            self.check_stmt(s.body, local)
            return

        # REPEAT
        if isinstance(s, Repeat):
            for st in s.body:
                self.check_stmt(st, local)
            t = self.check_expr(s.until_cond, local)
            if t != "boolean":
                raise SemanticError(11, "until должно быть boolean")
            return

        # WRITELN
        if isinstance(s, Writeln):
            for a in s.args:
                self.check_expr(a, local)
            return

        # READLN
        if isinstance(s, Readln):
            for name in s.args:
                if name not in self.sym and name not in local:
                    raise SemanticError(6, f"Идентификатор {name} не объявлен")
            return

        # CALL
        if isinstance(s, Call):
            if s.name not in self.subs:
                raise SemanticError(6, f"Подпрограмма {s.name} не объявлена")

            sub = self.subs[s.name]
            if len(s.args) != len(sub.params):
                raise SemanticError(7, "Неверное количество аргументов")

            for arg, param in zip(s.args, sub.params):
                t_arg = self.check_expr(arg, local)
                if not self.assignable(param.typ, t_arg):
                    raise SemanticError(7, f"Несовместимый тип параметра {param.name}")
            return

        raise SemanticError(7, "Неизвестный оператор")

    # =================================================================
    # EXPRESSION CHECK
    # =================================================================
    def check_expr(self, e: Expr, local) -> str:

        # ---------- Literals ----------
        if isinstance(e, Literal):
            return e.lit_type

        # ---------- Identifier ----------
        if isinstance(e, Identifier):
            return self.resolve_type(e.name, local)

        # ---------- Array Access ----------
        if isinstance(e, ArrayAccess):
            typ = self.resolve_type(e.name, local)
            if not isinstance(typ, ArrayType):
                raise SemanticError(7, f"{e.name} не является массивом")
            for idx in e.indexes:
                t = self.check_expr(idx, local)
                if t not in NUMERIC:
                    raise SemanticError(7, "Индекс массива должен быть числом")
            return typ.base_type

        # ---------- Unary ----------
        if isinstance(e, UnaryOp):
            t = self.check_expr(e.operand, local)
            if e.op == "not":
                if t != "boolean":
                    raise SemanticError(7, "not применим только к boolean")
                return "boolean"
            if e.op == "-":
                if t not in NUMERIC:
                    raise SemanticError(7, "Унарный минус только над числами")
                return t
            raise SemanticError(10, f"Неизвестный унарный оператор {e.op}")

        # ---------- Binary ----------
        if isinstance(e, BinaryOp):
            tl = self.check_expr(e.left, local)
            tr = self.check_expr(e.right, local)
            op = e.op

            # ============================
            #      STRING CONCAT
            # ============================
            if op == "+":
                # string + string
                if tl == "string" and tr == "string":
                    return "string"

                # string + char, char + string
                if (tl == "string" and tr == "char") or (tl == "char" and tr == "string"):
                    return "string"

                # string + numeric, numeric + string
                if (tl == "string" and tr in NUMERIC) or (tr == "string" and tl in NUMERIC):
                    return "string"

            # ============================
            #     NUMERIC ARITHMETIC
            # ============================
            if op in {"+", "-", "*", "/", "mod"}:
                if tl not in NUMERIC or tr not in NUMERIC:
                    raise SemanticError(7, "Арифметика только над числами")
                return "real" if "real" in (tl, tr) else "integer"

            # ---------- Logical ----------
            if op in {"and", "or"}:
                if tl != "boolean" or tr != "boolean":
                    raise SemanticError(7, "Логика только над boolean")
                return "boolean"

            # ---------- Comparison ----------
            if op in {"=", "<>", "<", ">", "<=", ">="}:
                if (tl in NUMERIC and tr in NUMERIC) or (tl == tr):
                    return "boolean"
                raise SemanticError(7, "Несовместимые типы при сравнении")

            raise SemanticError(10, f"Неизвестный оператор {op}")

        # ---------- Function Call ----------
        if isinstance(e, Call):
            if e.name not in self.subs:
                raise SemanticError(6, f"Функция {e.name} не объявлена")

            sub = self.subs[e.name]
            if not isinstance(sub, FunctionDecl):
                raise SemanticError(7, f"{e.name} не является функцией")

            if len(e.args) != len(sub.params):
                raise SemanticError(7, f"Неверное число аргументов функции {e.name}")

            for a, p in zip(e.args, sub.params):
                t = self.check_expr(a, local)
                if not self.assignable(p.typ, t):
                    raise SemanticError(7, f"Несовместимый тип параметра {p.name}")

            return sub.ret_type

        raise SemanticError(7, "Неизвестное выражение")

    # =================================================================
    # HELPERS
    # =================================================================
    def resolve_type(self, name: str, local) -> str | ArrayType:
        if name in local:
            return local[name]
        if name in self.sym:
            return self.sym[name]
        raise SemanticError(6, f"Идентификатор {name} не объявлен")

    def resolve_var(self, target, local):
        if isinstance(target, str):
            return self.resolve_type(target, local)
        if isinstance(target, ArrayAccess):
            typ = self.resolve_type(target.name, local)
            if not isinstance(typ, ArrayType):
                raise SemanticError(7, f"{target.name} не является массивом")
            return typ.base_type
        raise SemanticError(7, "Неверная левая часть присваивания")

    def assignable(self, left, right) -> bool:
        if left == right:
            return True
        if left == "real" and right == "integer":
            return True
        return False
