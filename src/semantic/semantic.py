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
        self.sym: Dict[str, Union[str, ArrayType, RecordType]] = {}
        self.subs: Dict[str, SubroutineDecl] = {}
        self.consts: Dict[str, str] = {}
        self.types: Dict[str, Union[str, RecordType]] = {}
        self.current_function: str | None = None


    def check(self, prog: Program):
        for c in prog.const_decls:
            if c.name in self.sym or c.name in self.consts:
                raise SemanticError(4, "Повторное объявление константы")
            self.consts[c.name] = c.typ


        for td in prog.type_decls:
            if td.name in self.types:
                if isinstance(td.typ, ClassDecl):
                    raise SemanticError(4, "Повторное объявление класса")
                raise SemanticError(4, "Повторное объявление типа")
            self.types[td.name] = td.typ

        for td in prog.type_decls:
            if isinstance(td.typ, RecordType):
                seen: set = set()
                for field in td.typ.fields:
                    self._resolve_declared_type(field.typ, context="field")
                    for fname in field.names:
                        if fname in seen:
                            raise SemanticError(4, f"Повторное объявление поля")
                        seen.add(fname)
            elif isinstance(td.typ, ClassDecl):
                seen_cls: set = set()
                for field in td.typ.fields:
                    self._resolve_declared_type(field.typ, context="field")
                    for fname in field.names:
                        if fname in seen_cls:
                            raise SemanticError(4, f"Повторное объявление поля")
                        seen_cls.add(fname)


        for d in prog.decls:
            for name in d.names:
                if name in self.sym:
                    raise SemanticError(4, f"Повторное объявление переменной")
                self.sym[name] = self._resolve_declared_type(d.typ)


        for sub in prog.subroutines:
            if isinstance(sub, MethodImpl):
                continue
            if sub.name in self.subs:
                raise SemanticError(4, f"Повторное объявление подпрограммы {sub.name}")
            self.subs[sub.name] = sub

        implemented_methods: set = set()
        for sub in prog.subroutines:
            if isinstance(sub, MethodImpl):
                key = (sub.class_name, sub.method_name)
                if key in implemented_methods:
                    raise SemanticError(4, f"Повторная реализация метода {sub.class_name}.{sub.method_name}")
                implemented_methods.add(key)
                self._check_method_impl(sub)
            else:
                self.check_subroutine(sub)

        self.check_block(prog.body)


    _BUILTIN_TYPES = {"integer", "real", "char", "boolean", "string"}
    def _resolve_declared_type(self, typ, context: str = "var"):
        """Resolve a declared type: expand string type names to their definitions."""
        if isinstance(typ, str):
            if typ in self.types:
                resolved = self.types[typ]
                if isinstance(resolved, ClassDecl):
                    return typ
                return resolved
            if typ not in self._BUILTIN_TYPES:
                if context == "field":
                    raise SemanticError(5, "Ожидался тип поля")
                raise SemanticError(5, "Ожидался тип данных")
        return typ


    def _check_method_impl(self, sub: MethodImpl):
        local = {}
        cls_typ = self.types.get(sub.class_name)
        if not isinstance(cls_typ, ClassDecl):
            raise SemanticError(6, "Класс не объявлен")

        method_names = [m.name for m in cls_typ.methods]
        if sub.method_name not in method_names:
            raise SemanticError(6, "Метод не объявлен в классе")
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


    def check_subroutine(self, sub: SubroutineDecl):
        local = {}
        for p in sub.params:
            if p.name in local:
                raise SemanticError(4, f"Повтор параметра {p.name}")
            local[p.name] = p.typ

        saved = self.current_function
        if isinstance(sub, FunctionDecl):
            self.current_function = sub.name
            local[sub.name] = sub.ret_type
        elif isinstance(sub, ProcedureDecl):

            self.current_function = None
            self._check_procedure_return(sub.body, sub.name)

        self.check_block(sub.body, local)


        if isinstance(sub, FunctionDecl):
            if not self._has_return(sub.body, sub.name):
                raise SemanticError(9, "Функция должна возвращать значение")

        self.current_function = saved

    def _check_procedure_return(self, block: Block, name: str):
        """Проверяет что процедура не присваивает значение через своё имя."""
        for stmt in block.statements:
            if isinstance(stmt, Assign) and isinstance(stmt.target, str) and stmt.target == name:
                raise SemanticError(9, "Процедура не может возвращать значение")
            if isinstance(stmt, Block):
                self._check_procedure_return(stmt, name)
            if isinstance(stmt, If):
                self._check_procedure_return(stmt.then_branch, name)
                if stmt.else_branch:
                    self._check_procedure_return(stmt.else_branch, name)

    def _has_return(self, block: Block, fname: str) -> bool:
        for stmt in block.statements:
            if isinstance(stmt, Assign) and isinstance(stmt.target, str) and stmt.target == fname:
                return True
            if isinstance(stmt, Block) and self._has_return(stmt, fname):
                return True
            if isinstance(stmt, If):
                if self._has_return(stmt.then_branch, fname):
                    return True
        return False


    def check_block(self, block: Block, local: Dict[str, str] | None = None):
        if local is None:
            local = {}
        for stmt in block.statements:
            self.check_stmt(stmt, local)

    def _check_counter_modification(self, stmt: Stmt, var: str):
        if isinstance(stmt, Assign) and stmt.target == var:
            raise SemanticError(11, "Изменение счётчика внутри цикла")
        if isinstance(stmt, Block):
            for st in stmt.statements:
                self._check_counter_modification(st, var)
        if isinstance(stmt, If):
            self._check_counter_modification(stmt.then_branch, var)
            if stmt.else_branch:
                self._check_counter_modification(stmt.else_branch, var)
        if isinstance(stmt, While):
            self._check_counter_modification(stmt.body, var)
        if isinstance(stmt, For):
            self._check_counter_modification(stmt.body, var)


    def check_stmt(self, s: Stmt, local):
        if isinstance(s, Block):
            self.check_block(s, local)
            return

        if isinstance(s, Assign):
            if isinstance(s.target, str) and s.target in self.consts:
                raise SemanticError(9, "Изменение значения константы")

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

            if isinstance(t_left, ArrayType):
                raise SemanticError(7, "Ожидался индекс массива")
            t_right = self.check_expr(s.expr, local)
            if not self.assignable(t_left, t_right):
                raise SemanticError(7, "Недопустимое преобразование типов")
            return

        if isinstance(s, If):
            cond = self.check_expr(s.cond, local)
            if cond != "boolean":
                raise SemanticError(11, "Ожидалось логическое выражение")
            self.check_stmt(s.then_branch, local)
            if s.else_branch:
                self.check_stmt(s.else_branch, local)
            return

        if isinstance(s, While):
            cond = self.check_expr(s.cond, local)
            if cond != "boolean":
                raise SemanticError(11, "Ожидалось логическое выражение")
            self.check_stmt(s.body, local)
            return

        if isinstance(s, For):
            if s.var not in self.sym and s.var not in local:
                raise SemanticError(6, "Неизвестный идентификатор счётчика")
            var_type = self.resolve_type(s.var, local)
            if var_type != "integer":
                raise SemanticError(11, "Счётчик цикла должен быть целым")
            t_start = self.check_expr(s.start, local)
            t_end = self.check_expr(s.end, local)
            if t_start != "integer" or t_end != "integer":
                raise SemanticError(11, "Граница цикла должна быть целым числом")

            if (isinstance(s.start, Literal) and isinstance(s.end, Literal)
                    and s.direction == "to"
                    and isinstance(s.start.value, (int, float))
                    and isinstance(s.end.value, (int, float))
                    and s.start.value > s.end.value):
                raise SemanticError(11, "Начальное значение превышает конечное")

            self._check_counter_modification(s.body, s.var)
            self.check_stmt(s.body, local)
            return

        if isinstance(s, Repeat):
            for st in s.body:
                self.check_stmt(st, local)
            t = self.check_expr(s.until_cond, local)
            if t != "boolean":
                raise SemanticError(11, "Ожидалось логическое выражение")
            return

        if isinstance(s, Case):
            t_expr = self.check_expr(s.expr, local)
            seen_labels = set()
            for branch in s.branches:
                for val in branch.values:
                    t_val = self.check_expr(val, local)

                    if t_val != t_expr:
                        raise SemanticError(7, "Тип метки не совпадает с типом выражения")

                    key = val.value if isinstance(val, Literal) else None
                    if key is not None:
                        if key in seen_labels:
                            raise SemanticError(7, "Метка выбора уже использовалась в этом блоке")
                        seen_labels.add(key)
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
                    raise SemanticError(6, "Неизвестный идентификатор")
            return

        if isinstance(s, MethodCall):
            if s.obj not in self.sym and s.obj not in local:
                raise SemanticError(6, "Вызов метода на необъявленном объекте")
            obj_type = self.resolve_type(s.obj, local)
            if isinstance(obj_type, str) and obj_type in self.types:
                cls = self.types[obj_type]
                if isinstance(cls, ClassDecl):
                    method_names = [m.name for m in cls.methods]
                    if s.method not in method_names:
                        raise SemanticError(6, "Обращение к несуществующему методу")
            return

        if isinstance(s, Call):
            if s.name not in self.subs:
                raise SemanticError(6, "Вызов необъявленной подпрограммы")
            sub = self.subs[s.name]
            if len(s.args) != len(sub.params):
                raise SemanticError(7, "Неверное количество параметров")
            for arg, param in zip(s.args, sub.params):
                t_arg = self.check_expr(arg, local)
                if not self.assignable(param.typ, t_arg):
                    raise SemanticError(7, "Несоответствие типов аргументов")
            return

        raise SemanticError(7, "Неизвестный оператор")


    def check_expr(self, e: Expr, local) -> str:
        if isinstance(e, Literal):
            return e.lit_type

        if isinstance(e, Identifier):
            name = e.name

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
            raise SemanticError(6, "Обращение к несуществующему полю")

        if isinstance(e, ArrayAccess):
            typ = self.resolve_type(e.name, local)
            if not isinstance(typ, ArrayType):
                raise SemanticError(7, "Ожидался индекс массива")
            for i, idx in enumerate(e.indexes):
                t = self.check_expr(idx, local)
                if t != "integer":
                    raise SemanticError(7, "Индекс должен быть целым")

                if isinstance(idx, Literal) and isinstance(idx.value, int) and i < len(typ.ranges):
                    lo, hi = typ.ranges[i]
                    if idx.value < lo or idx.value > hi:
                        raise SemanticError(7, "Индекс вне границ массива")
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

            if op == "mod":
                if tl != "integer" or tr != "integer":
                    raise SemanticError(7, "Недопустимая операция для данного типа")
                return "integer"

            if op == "/":
                if isinstance(e.right, Literal) and e.right.value == 0:
                    raise SemanticError(7, "Деление на 0")
                if tl not in NUMERIC or tr not in NUMERIC:
                    raise SemanticError(7, "Несовместимые типы")
                return "real"

            if op in {"+", "-", "*"}:
                if tl == "string" or tr == "string":
                    raise SemanticError(7, "Недопустимая операция для строки")
                if tl not in NUMERIC or tr not in NUMERIC:
                    raise SemanticError(7, "Несовместимые типы")
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
            cls_typ = self.types.get(e.class_name)
            if not isinstance(cls_typ, ClassDecl):
                raise SemanticError(6, "Класс не объявлен")
            constructor = next((m for m in cls_typ.methods if m.kind == "constructor"), None)
            if constructor is None:
                raise SemanticError(6, "Конструктор не объявлен")
            if len(e.args) != len(constructor.params):
                raise SemanticError(7, "Неверное количество аргументов конструктора")
            for arg, param in zip(e.args, constructor.params):
                t = self.check_expr(arg, local)
                if not self.assignable(param.typ, t):
                    raise SemanticError(7, "Несоответствие типов аргументов конструктора")
            return e.class_name

        if isinstance(e, Call):
            if e.name not in self.subs:
                raise SemanticError(6, "Вызов необъявленной подпрограммы")
            sub = self.subs[e.name]
            if not isinstance(sub, FunctionDecl):
                raise SemanticError(7, f"{e.name} не является функцией")
            if len(e.args) != len(sub.params):
                raise SemanticError(7, "Неверное количество параметров")
            for a, p in zip(e.args, sub.params):
                t = self.check_expr(a, local)
                if not self.assignable(p.typ, t):
                    raise SemanticError(7, "Несоответствие типов аргументов")
            return sub.ret_type

        raise SemanticError(7, "Неизвестное выражение")


    def resolve_type(self, name: str, local) -> str | ArrayType | RecordType:
        if name in local:
            t = local[name]
            return self._resolve_declared_type(t)
        if name in self.sym:
            return self.sym[name]
        if name in self.consts:
            return self.consts[name]
        raise SemanticError(6, "Неизвестный идентификатор")

    def resolve_var(self, target, local):
        if isinstance(target, str):
            return self.resolve_type(target, local)
        if isinstance(target, FieldAccess):
            obj_type = self.resolve_type(target.obj, local)
            rec = self._as_record(target.obj, obj_type)
            for field_decl in rec.fields:
                if target.field in field_decl.names:
                    return field_decl.typ if isinstance(field_decl.typ, str) else "record"
            raise SemanticError(6, "Обращение к несуществующему полю")
        if isinstance(target, ArrayAccess):
            typ = self.resolve_type(target.name, local)
            if not isinstance(typ, ArrayType):
                raise SemanticError(7, "Ожидался индекс массива")
            for i, idx in enumerate(target.indexes):
                t = self.check_expr(idx, local)
                if t != "integer":
                    raise SemanticError(7, "Индекс должен быть целым")
                if isinstance(idx, Literal) and isinstance(idx.value, int) and i < len(typ.ranges):
                    lo, hi = typ.ranges[i]
                    if idx.value < lo or idx.value > hi:
                        raise SemanticError(7, "Индекс вне границ массива")
            return typ.base_type
        raise SemanticError(7, "Неверная левая часть присваивания")

    def _as_record(self, name: str, typ) -> RecordType:
        if isinstance(typ, RecordType):
            return typ
        if isinstance(typ, str) and typ in self.types:
            t = self.types[typ]
            if isinstance(t, RecordType):
                return t
            if isinstance(t, ClassDecl):

                return RecordType(t.fields)
        raise SemanticError(7, f"'{name}' не является записью (record)")

    def assignable(self, left, right) -> bool:
        if left == right:
            return True
        if left == "real" and right == "integer":
            return True
        return False