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
            sub.accept(self)
        
        prog.body.accept(self)
    
    def visit_const_decl(self, node: ConstDecl):
        if node.name in self.sym or node.name in self.consts:
            raise SemanticError(4, f"Повторное объявление {node.name}")
        self.consts[node.name] = node.typ
    
    def visit_type_decl(self, node: TypeDecl):
        if node.name in self.types:
            raise SemanticError(4, f"Повторное объявление типа {node.name}")
        self.types[node.name] = node.typ
    
    def visit_var_decl(self, node: VarDecl):
        for name in node.names:
            if name in self.sym:
                raise SemanticError(4, f"Повторное объявление {name}")
            self.sym[name] = self._resolve_declared_type(node.typ)
    
    def visit_record_type(self, node: RecordType):
        for field in node.fields:
            field.accept(self)
    
    def visit_array_type(self, node: ArrayType):
        pass
    
    def visit_param(self, node: Param):
        pass
    
    def visit_procedure_decl(self, node: ProcedureDecl):
        if node.name in self.subs:
            raise SemanticError(4, f"Повторное объявление подпрограммы {node.name}")
        self.subs[node.name] = node
        self._check_subroutine(node)
    
    def visit_function_decl(self, node: FunctionDecl):
        if node.name in self.subs:
            raise SemanticError(4, f"Повторное объявление подпрограммы {node.name}")
        self.subs[node.name] = node
        self._check_subroutine(node)
    
    def visit_block(self, node: Block):
        for stmt in node.statements:
            stmt.accept(self)
    
    def visit_assign(self, node: Assign):
        if isinstance(node.target, str) and node.target == self.current_function:
            t_right = self._check_expr(node.expr)
            t_expected = self.local_vars[node.target]
            if not self._assignable(t_expected, t_right):
                raise SemanticError(7, f"Тип возврата функции {self.current_function} должен быть {t_expected}")
            return
        
        t_left = self._resolve_var(node.target)
        t_right = self._check_expr(node.expr)
        if not self._assignable(t_left, t_right):
            raise SemanticError(7, f"Несовместимые типы: {t_left} := {t_right}")
    
    def visit_if(self, node: If):
        cond = self._check_expr(node.cond)
        if cond != "boolean":
            raise SemanticError(11, "Условие if должно быть boolean")
        node.then_branch.accept(self)
        if node.else_branch:
            node.else_branch.accept(self)
    
    def visit_while(self, node: While):
        cond = self._check_expr(node.cond)
        if cond != "boolean":
            raise SemanticError(11, "Условие while должно быть boolean")
        node.body.accept(self)
    
    def visit_for(self, node: For):
        if node.var not in self.sym and node.var not in self.local_vars:
            raise SemanticError(6, f"Идентификатор {node.var} не объявлен")
        var_type = self._resolve_type(node.var)
        if var_type not in NUMERIC:
            raise SemanticError(11, "Переменная for должна быть числовой")
        t_start = self._check_expr(node.start)
        t_end = self._check_expr(node.end)
        if t_start not in NUMERIC or t_end not in NUMERIC:
            raise SemanticError(11, "Границы for должны быть числовыми")
        node.body.accept(self)
    
    def visit_repeat(self, node: Repeat):
        for st in node.body:
            st.accept(self)
        t = self._check_expr(node.until_cond)
        if t != "boolean":
            raise SemanticError(11, "until должно быть boolean")
    
    def visit_case_branch(self, node: CaseBranch):
        for val in node.values:
            self._check_expr(val)
        node.stmt.accept(self)
    
    def visit_case(self, node: Case):
        self._check_expr(node.expr)
        for branch in node.branches:
            branch.accept(self)
        if node.else_branch:
            node.else_branch.accept(self)
    
    def visit_writeln(self, node: Writeln):
        for a in node.args:
            self._check_expr(a)
    
    def visit_readln(self, node: Readln):
        for name in node.args:
            if name not in self.sym and name not in self.local_vars:
                raise SemanticError(6, f"Идентификатор {name} не объявлен")
    
    def visit_call(self, node: Call):
        if node.name not in self.subs:
            raise SemanticError(6, f"Подпрограмма {node.name} не объявлена")
        sub = self.subs[node.name]
        
        if not isinstance(sub, (ProcedureDecl, FunctionDecl)):
            raise SemanticError(7, f"{node.name} не является подпрограммой")
        
        if len(node.args) != len(sub.params):
            raise SemanticError(7, "Неверное количество аргументов")
        for arg, param in zip(node.args, sub.params):
            t_arg = self._check_expr(arg)
            if not self._assignable(param.typ, t_arg):
                raise SemanticError(7, f"Несовместимый тип параметра {param.name}")
        
        if isinstance(sub, FunctionDecl):
            return sub.ret_type
        return None
    
    def visit_literal(self, node: Literal):
        return node.lit_type
    
    def visit_identifier(self, node: Identifier):
        return self._resolve_type(node.name)
    
    def visit_field_access(self, node: FieldAccess):
        obj_type = self._resolve_type(node.obj)
        rec = self._as_record(node.obj, obj_type)
        for field_decl in rec.fields:
            if node.field in field_decl.names:
                ft = field_decl.typ
                if isinstance(ft, str) and ft in self.types:
                    return self._resolve_declared_type(ft)
                return ft if isinstance(ft, str) else "record"
        raise SemanticError(6, f"Поле '{node.field}' не найдено в записи")
    
    def visit_array_access(self, node: ArrayAccess):
        typ = self._resolve_type(node.name)
        if not isinstance(typ, ArrayType):
            raise SemanticError(7, f"{node.name} не является массивом")
        for idx in node.indexes:
            t = self._check_expr(idx)
            if t not in NUMERIC:
                raise SemanticError(7, "Индекс массива должен быть числом")
        return typ.base_type
    
    def visit_unary_op(self, node: UnaryOp):
        t = self._check_expr(node.operand)
        if node.op == "not":
            if t != "boolean":
                raise SemanticError(7, "not применим только к boolean")
            return "boolean"
        if node.op == "-":
            if t not in NUMERIC:
                raise SemanticError(7, "Унарный минус только над числами")
            return t
        raise SemanticError(10, f"Неизвестный унарный оператор {node.op}")
    
    def visit_binary_op(self, node: BinaryOp):
        tl = self._check_expr(node.left)
        tr = self._check_expr(node.right)
        op = node.op

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
    
    # =================================================================
    # HELPER METHODS
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