from __future__ import annotations
from typing import Dict, Union
from src.ast.ast_nodes import *
from src.errors import SemanticError
from src.visitors.visitor import ASTVisitor

from src.ast.ast_nodes import (
    Program, ConstDecl, TypeDecl, VarDecl, RecordType, ArrayType,
    Param, ProcedureDecl, FunctionDecl, Block, Assign, If, While,
    For, Repeat, Case, CaseBranch, Writeln, Readln, Call,
    Literal, Identifier, FieldAccess, ArrayAccess, UnaryOp, BinaryOp,
    SubroutineDecl, Expr, Stmt
)

NUMERIC = {"integer", "real"}
BOOL = {"boolean"}
CHAR = {"char"}
STRING = {"string"}

class SemanticChecker(ASTVisitor):
    def __init__(self):
        self.sym: Dict[str, Union[str, ArrayType, RecordType]] = {}
        self.subs: Dict[str, SubroutineDecl] = {}
        self.consts: Dict[str, str] = {}
        self.types: Dict[str, Union[str, RecordType]] = {}
        self.current_function: str | None = None
        self.local_vars: Dict[str, str] = {}

    # =================================================================
    # MAIN ENTRY
    # =================================================================
    def check(self, prog: Program):
        prog.accept(self)

    # =================================================================
    # VISITOR METHODS
    # =================================================================
    
    def visit_program(self, prog: Program):
        for c in prog.const_decls:
            c.accept(self)
        
        for td in prog.type_decls:
            td.accept(self)
        
        for d in prog.decls:
            d.accept(self)
        
        for sub in prog.subroutines:
            if isinstance(sub, MethodImpl):
                continue
            if sub.name in self.subs:
                raise SemanticError(4, f"Повторное объявление подпрограммы {sub.name}")
            self.subs[sub.name] = sub

        for sub in prog.subroutines:
            if isinstance(sub, MethodImpl):
                self._check_method_impl(sub)
            else:
                self.check_subroutine(sub)

        self.check_block(prog.body)

    # =================================================================
    # RESOLVE TYPE (handles user-defined type aliases)
    # =================================================================
    def _resolve_declared_type(self, typ):
        """Resolve a declared type: expand string type names to their definitions."""
        if isinstance(typ, str) and typ in self.types:
            resolved = self.types[typ]
            if isinstance(resolved, ClassDecl):
                return typ  # keep class types as their name string
            return resolved
        return typ

        raise SemanticError(10, f"Неизвестный оператор {op}")
    
    # =================================================================
    # METHOD IMPL
    # =================================================================
    def _check_method_impl(self, sub: MethodImpl):
        local = {}
        # add class fields to local scope
        cls_typ = self.types.get(sub.class_name)
        if isinstance(cls_typ, ClassDecl):
            for field in cls_typ.fields:
                for n in field.names:
                    local[n] = field.typ
        for p in sub.params:
            local[p.name] = p.typ
        saved = self.current_function
        if sub.kind == "function":
            self.current_function = sub.method_name
            local[sub.method_name] = sub.ret_type
        self.check_block(sub.body, local)
        self.current_function = saved

    # =================================================================
    # SUBROUTINES
    # =================================================================
    
    def _check_subroutine(self, sub: SubroutineDecl):
        if not isinstance(sub, (ProcedureDecl, FunctionDecl)):
            raise SemanticError(7, "Ошибка в объявлении подпрограммы")
        
        local = {}
        for p in sub.params:
            if p.name in local:
                raise SemanticError(4, f"Повтор параметра {p.name}")
            local[p.name] = p.typ
        
        saved = self.current_function
        saved_local = self.local_vars
        
        if isinstance(sub, FunctionDecl):
            self.current_function = sub.name
            local[sub.name] = sub.ret_type
        
        self.local_vars = local
        sub.body.accept(self)
        
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
        if isinstance(s, Block):
            self.check_block(s, local)
            return

        if isinstance(s, Assign):
            if isinstance(s.target, str) and s.target == self.current_function:
                t_right = self.check_expr(s.expr, local)
                t_expected = local[s.target]
                if not self.assignable(t_expected, t_right):
                    raise SemanticError(
                        7,
                        f"Тип возврата функции {self.current_function} должен быть {t_expected}"
                    )
                return

            t_left = self.resolve_var(s.target, local)
            t_right = self.check_expr(s.expr, local)
            if not self.assignable(t_left, t_right):
                raise SemanticError(7, f"Несовместимые типы: {t_left} := {t_right}")
            return

        if isinstance(s, If):
            cond = self.check_expr(s.cond, local)
            if cond != "boolean":
                raise SemanticError(11, "Условие if должно быть boolean")
            self.check_stmt(s.then_branch, local)
            if s.else_branch:
                self.check_stmt(s.else_branch, local)
            return

        if isinstance(s, While):
            cond = self.check_expr(s.cond, local)
            if cond != "boolean":
                raise SemanticError(11, "Условие while должно быть boolean")
            self.check_stmt(s.body, local)
            return

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

        if isinstance(s, Repeat):
            for st in s.body:
                self.check_stmt(st, local)
            t = self.check_expr(s.until_cond, local)
            if t != "boolean":
                raise SemanticError(11, "until должно быть boolean")
            return

        if isinstance(s, Case):
            self.check_expr(s.expr, local)
            for branch in s.branches:
                for val in branch.values:
                    self.check_expr(val, local)
                self.check_stmt(branch.stmt, local)
            if s.else_branch:
                self.check_stmt(s.else_branch, local)
            return

        if isinstance(s, Writeln):
            for a in s.args:
                self.check_expr(a, local)
            return

        if isinstance(s, Readln):
            for name in s.args:
                if name not in self.sym and name not in local:
                    raise SemanticError(6, f"Идентификатор {name} не объявлен")
            return

        if isinstance(s, MethodCall):
            return  # валидация методов на уровне C++ компилятора

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
        if isinstance(e, Literal):
            return e.lit_type

        if isinstance(e, Identifier):
            name = e.name
            # check consts too
            if name in self.consts:
                return self.consts[name]
            return self.resolve_type(name, local)

        if isinstance(e, FieldAccess):
            obj_type = self.resolve_type(e.obj, local)
            rec = self._as_record(e.obj, obj_type)
            for field_decl in rec.fields:
                if e.field in field_decl.names:
                    ft = field_decl.typ
                    if isinstance(ft, str) and ft in self.types:
                        return ft
                    return ft if isinstance(ft, str) else "record"
            raise SemanticError(6, f"Поле '{e.field}' не найдено в записи")

        if isinstance(e, ArrayAccess):
            typ = self.resolve_type(e.name, local)
            if not isinstance(typ, ArrayType):
                raise SemanticError(7, f"{e.name} не является массивом")
            for idx in e.indexes:
                t = self.check_expr(idx, local)
                if t not in NUMERIC:
                    raise SemanticError(7, "Индекс массива должен быть числом")
            return typ.base_type

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

        if isinstance(e, BinaryOp):
            tl = self.check_expr(e.left, local)
            tr = self.check_expr(e.right, local)
            op = e.op

            if op == "+":
                if tl == "string" and tr == "string":
                    return "string"
                if (tl == "string" and tr == "char") or (tl == "char" and tr == "string"):
                    return "string"
                if (tl == "string" and tr in NUMERIC) or (tr == "string" and tl in NUMERIC):
                    return "string"

            if op in {"+", "-", "*", "/", "mod"}:
                if tl not in NUMERIC or tr not in NUMERIC:
                    raise SemanticError(7, "Арифметика только над числами")
                return "real" if "real" in (tl, tr) else "integer"

            if op in {"and", "or"}:
                if tl != "boolean" or tr != "boolean":
                    raise SemanticError(7, "Логика только над boolean")
                return "boolean"

            if op in {"=", "<>", "<", ">", "<=", ">="}:
                if (tl in NUMERIC and tr in NUMERIC) or (tl == tr):
                    return "boolean"
                raise SemanticError(7, "Несовместимые типы при сравнении")

            raise SemanticError(10, f"Неизвестный оператор {op}")

        if isinstance(e, MethodCall):
            return "object"

        if isinstance(e, ObjectCreate):
            return e.class_name

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
    def resolve_type(self, name: str, local) -> str | ArrayType | RecordType:
        if name in local:
            t = local[name]
        self.local_vars = saved_local
    
    def _check_expr(self, e: Expr) -> str:
        return e.accept(self)
    
    def _resolve_declared_type(self, typ):
        if isinstance(typ, str) and typ in self.types:
            return self.types[typ]
        return typ
    
    def _resolve_type(self, name: str):
        if name in self.local_vars:
            t = self.local_vars[name]

            return self._resolve_declared_type(t)
        if name in self.sym:
            return self.sym[name]
        if name in self.consts:
            return self.consts[name]
        raise SemanticError(6, f"Идентификатор '{name}' не объявлен")
    
    def _resolve_var(self, target):
        if isinstance(target, str):
            return self._resolve_type(target)
        if isinstance(target, FieldAccess):
            return target.accept(self)
        if isinstance(target, ArrayAccess):
            return target.accept(self)
        raise SemanticError(7, "Неверная левая часть присваивания")
    
    def _as_record(self, name: str, typ):
        if isinstance(typ, RecordType):
            return typ
        if isinstance(typ, str) and typ in self.types:
            t = self.types[typ]
            if isinstance(t, RecordType):
                return t
        raise SemanticError(7, f"'{name}' не является записью (record)")
    
    def _assignable(self, left, right) -> bool:
        if left == right:
            return True
        if left == "real" and right == "integer":
            return True
        return False