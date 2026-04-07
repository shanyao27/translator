from __future__ import annotations
from typing import List
from src.tokens import Token, TokType, TYPE_KEYWORDS
from src.errors import ParseError
from src.ast.ast_nodes import *


class Parser:
    def __init__(self, tokens: List[Token]):
        self.toks = tokens
        self.i = 0

    def cur(self) -> Token:
        return self.toks[self.i]

    def eat(self, t: TokType | None = None, v: str | None = None) -> Token:
        tok = self.cur()
        if t is not None and tok.type != t:
            raise ParseError(7, f"Ожидалось {t}, получено {tok.type}", tok.line, tok.col)
        if v is not None and tok.value != v:
            raise ParseError(7, f"Ожидалось '{v}', получено '{tok.value}'", tok.line, tok.col)
        self.i += 1
        return tok

    def match(self, t: TokType | None = None, v: str | None = None) -> bool:
        tok = self.cur()
        if t is not None and tok.type != t:
            return False
        if v is not None and tok.value != v:
            return False
        return True

    # ======================================================
    # PROGRAM
    # ======================================================
    def parse_program(self) -> Program:
        self.eat(TokType.KEYWORD, "program")
        name = self.eat(TokType.IDENT).value
        self.eat(TokType.DELIM, ";")

        const_decls = self.parse_consts()
        type_decls = self.parse_type_decls()
        decls = self.parse_decls()
        subs = self.parse_subroutines()

        self.eat(TokType.KEYWORD, "begin")
        body = self.parse_block_body()
        self.eat(TokType.KEYWORD, "end")
        self.eat(TokType.DELIM, ".")
        self.eat(TokType.EOF)

        return Program(name, const_decls, type_decls, decls, subs, body)

    # ======================================================
    # CONST DECLARATIONS
    # ======================================================
    def parse_consts(self) -> List[ConstDecl]:
        consts = []
        if not self.match(TokType.KEYWORD, "const"):
            return consts
        self.eat(TokType.KEYWORD, "const")
        while self.match(TokType.IDENT):
            name = self.eat(TokType.IDENT).value
            self.eat(TokType.OP, "=")

            neg = False
            if self.match(TokType.OP, "-"):
                self.eat(TokType.OP, "-")
                neg = True

            tok = self.cur()
            if tok.type == TokType.INT:
                v = int(self.eat(TokType.INT).value)
                val = Literal(-v if neg else v, "integer")
            elif tok.type == TokType.REAL:
                v = float(self.eat(TokType.REAL).value)
                val = Literal(-v if neg else v, "real")
            elif tok.type == TokType.STRING:
                if neg:
                    raise ParseError(5, "Унарный минус неприменим к строке", tok.line, tok.col)
                val = Literal(self.eat(TokType.STRING).value, "string")
            elif tok.type == TokType.CHAR:
                if neg:
                    raise ParseError(5, "Унарный минус неприменим к символу", tok.line, tok.col)
                val = Literal(self.eat(TokType.CHAR).value, "char")
            elif tok.type == TokType.BOOL:
                if neg:
                    raise ParseError(5, "Унарный минус неприменим к boolean", tok.line, tok.col)
                val = Literal(self.eat(TokType.BOOL).value == "true", "boolean")
            else:
                raise ParseError(5, "Ожидалась константа", tok.line, tok.col)

            self.eat(TokType.DELIM, ";")
            consts.append(ConstDecl(name, val, val.lit_type))
        return consts

    # ======================================================
    # TYPE DECLARATIONS
    # ======================================================
    def parse_type_decls(self) -> List[TypeDecl]:
        type_decls = []
        if not self.match(TokType.KEYWORD, "type"):
            return type_decls
        self.eat(TokType.KEYWORD, "type")
        while self.match(TokType.IDENT):
            name = self.eat(TokType.IDENT).value
            self.eat(TokType.OP, "=")
            if self.match(TokType.KEYWORD, "record"):
                typ = self.parse_record_type()
            elif self.match(TokType.KEYWORD, "class"):
                typ = self.parse_class_type()
            else:
                typ = self.parse_type()
            self.eat(TokType.DELIM, ";")
            type_decls.append(TypeDecl(name, typ))
        return type_decls

    def parse_class_type(self) -> "ClassDecl":
        self.eat(TokType.KEYWORD, "class")
        fields = []
        methods = []
        while not self.match(TokType.KEYWORD, "end"):
            if self.match(TokType.KEYWORD, "constructor"):
                self.eat(TokType.KEYWORD, "constructor")
                name = self.eat(TokType.IDENT).value
                params = self.parse_param_list_opt()
                self.eat(TokType.DELIM, ";")
                methods.append(MethodSignature("constructor", name, params, None))
            elif self.match(TokType.KEYWORD, "procedure"):
                self.eat(TokType.KEYWORD, "procedure")
                name = self.eat(TokType.IDENT).value
                params = self.parse_param_list_opt()
                self.eat(TokType.DELIM, ";")
                methods.append(MethodSignature("procedure", name, params, None))
            elif self.match(TokType.KEYWORD, "function"):
                self.eat(TokType.KEYWORD, "function")
                name = self.eat(TokType.IDENT).value
                params = self.parse_param_list_opt()
                self.eat(TokType.DELIM, ":")
                ret_type = self.eat(TokType.KEYWORD).value
                self.eat(TokType.DELIM, ";")
                methods.append(MethodSignature("function", name, params, ret_type))
            else:
                fields.append(self.parse_decl())
        self.eat(TokType.KEYWORD, "end")
        return ClassDecl(fields, methods)

    def parse_record_type(self) -> RecordType:
        self.eat(TokType.KEYWORD, "record")
        fields = []
        while not self.match(TokType.KEYWORD, "end"):
            fields.append(self.parse_decl())
        self.eat(TokType.KEYWORD, "end")
        return RecordType(fields)

    # ======================================================
    # DECLARATIONS (var ...)
    # ======================================================
    def parse_decls(self) -> List[VarDecl]:
        decls = []
        if self.match(TokType.KEYWORD, "var"):
            self.eat(TokType.KEYWORD, "var")
            while not (self.match(TokType.KEYWORD, "begin")
                       or self.match(TokType.KEYWORD, "procedure")
                       or self.match(TokType.KEYWORD, "function")
                       or self.match(TokType.KEYWORD, "constructor")):
                decls.append(self.parse_decl())
        return decls

    def parse_decl(self) -> VarDecl:
        names = self.parse_id_list()
        self.eat(TokType.DELIM, ":")
        typ = self.parse_type()
        self.eat(TokType.DELIM, ";")
        return VarDecl(names, typ)

    def parse_id_list(self) -> List[str]:
        ids = [self.eat(TokType.IDENT).value]
        while self.match(TokType.DELIM, ","):
            self.eat(TokType.DELIM, ",")
            ids.append(self.eat(TokType.IDENT).value)
        return ids

    # ======================================================
    # TYPE PARSER (simple + array + user-defined)
    # ======================================================
    def parse_type(self):
        if self.match(TokType.KEYWORD, "array"):
            self.eat(TokType.KEYWORD, "array")
            self.eat(TokType.DELIM, "[")
            ranges = []

            while True:
                low = int(self.eat(TokType.INT).value)
                self.eat(TokType.OP, "..")
                high = int(self.eat(TokType.INT).value)
                ranges.append((low, high))
                if self.match(TokType.DELIM, ","):
                    self.eat(TokType.DELIM, ",")
                else:
                    break

            self.eat(TokType.DELIM, "]")
            self.eat(TokType.KEYWORD, "of")

            if not (self.match(TokType.KEYWORD) and self.cur().value in TYPE_KEYWORDS):
                raise ParseError(5, "Ожидался базовый тип массива")
            base = self.eat(TokType.KEYWORD).value
            return ArrayType(ranges, base)

        # user-defined type (record alias etc.)
        if self.match(TokType.IDENT):
            return self.eat(TokType.IDENT).value

        if not (self.match(TokType.KEYWORD) and self.cur().value in TYPE_KEYWORDS):
            raise ParseError(5, "Ожидался тип переменной")
        return self.eat(TokType.KEYWORD).value

    # ======================================================
    # SUBROUTINES
    # ======================================================
    def parse_subroutines(self) -> List[SubroutineDecl]:
        subs = []
        while (self.match(TokType.KEYWORD, "procedure")
               or self.match(TokType.KEYWORD, "function")
               or self.match(TokType.KEYWORD, "constructor")):
            kind = self.eat(TokType.KEYWORD).value
            name = self.eat(TokType.IDENT).value

            if self.match(TokType.DELIM, "."):
                # method implementation: procedure ClassName.MethodName
                self.eat(TokType.DELIM, ".")
                method_name = self.eat(TokType.IDENT).value
                params = self.parse_param_list_opt()
                ret_type = None
                if kind == "function":
                    self.eat(TokType.DELIM, ":")
                    ret_type = self.eat(TokType.KEYWORD).value
                self.eat(TokType.DELIM, ";")
                self.eat(TokType.KEYWORD, "begin")
                body = self.parse_block_body()
                self.eat(TokType.KEYWORD, "end")
                self.eat(TokType.DELIM, ";")
                subs.append(MethodImpl(name, method_name, kind, params, ret_type, body))
            elif kind == "procedure":
                params = self.parse_param_list_opt()
                self.eat(TokType.DELIM, ";")
                self.eat(TokType.KEYWORD, "begin")
                body = self.parse_block_body()
                self.eat(TokType.KEYWORD, "end")
                self.eat(TokType.DELIM, ";")
                subs.append(ProcedureDecl(name, params, body))
            elif kind == "function":
                params = self.parse_param_list_opt()
                self.eat(TokType.DELIM, ":")
                ret_type = self.eat(TokType.KEYWORD).value
                self.eat(TokType.DELIM, ";")
                self.eat(TokType.KEYWORD, "begin")
                body = self.parse_block_body()
                self.eat(TokType.KEYWORD, "end")
                self.eat(TokType.DELIM, ";")
                subs.append(FunctionDecl(name, params, ret_type, body))
        return subs

    def parse_param_list_opt(self) -> List[Param]:
        params = []
        if self.match(TokType.DELIM, "("):
            self.eat(TokType.DELIM, "(")
            while True:
                names = self.parse_id_list()
                self.eat(TokType.DELIM, ":")
                typ = self.eat(TokType.KEYWORD).value
                for n in names:
                    params.append(Param(n, typ))
                if self.match(TokType.DELIM, ";"):
                    self.eat(TokType.DELIM, ";")
                else:
                    break
            self.eat(TokType.DELIM, ")")
        return params

    # ======================================================
    # BLOCK
    # ======================================================
    def parse_block_body(self) -> Block:
        stmts = []
        while not self.match(TokType.KEYWORD, "end"):
            stmts.append(self.parse_statement())
            if self.match(TokType.DELIM, ";"):
                self.eat(TokType.DELIM, ";")
            else:
                if not self.match(TokType.KEYWORD, "end"):
                    raise ParseError(3, "Пропущен ;")
        return Block(stmts)

    # ======================================================
    # STATEMENTS
    # ======================================================
    def parse_statement(self) -> Stmt:
        tok = self.cur()

        if self.match(TokType.KEYWORD, "begin"):
            self.eat(TokType.KEYWORD, "begin")
            body = self.parse_block_body()
            self.eat(TokType.KEYWORD, "end")
            return body

        if self.match(TokType.KEYWORD, "if"):
            return self.parse_if()

        if self.match(TokType.KEYWORD, "while"):
            return self.parse_while()

        if self.match(TokType.KEYWORD, "for"):
            return self.parse_for()

        if self.match(TokType.KEYWORD, "repeat"):
            return self.parse_repeat()

        if self.match(TokType.KEYWORD, "case"):
            return self.parse_case()

        if self.match(TokType.KEYWORD, "writeln"):
            return self.parse_writeln()

        if self.match(TokType.KEYWORD, "readln"):
            return self.parse_readln()

        if self.match(TokType.IDENT):
            name = self.eat(TokType.IDENT).value

            # obj.something
            if self.match(TokType.DELIM, "."):
                self.eat(TokType.DELIM, ".")
                fname = self.eat(TokType.IDENT).value
                if self.match(TokType.DELIM, "("):
                    # obj.method(args)
                    args = self.parse_call_args()
                    return MethodCall(name, fname, args)
                if self.match(TokType.OP, ":="):
                    # obj.field := expr
                    self.eat(TokType.OP, ":=")
                    expr = self.parse_expression()
                    return Assign(FieldAccess(name, fname), expr)
                # obj.method  (no-arg method call)
                return MethodCall(name, fname, [])

            # array assignment: a[i] := expr
            if self.match(TokType.DELIM, "["):
                indexes = self.parse_array_indexes()
                self.eat(TokType.OP, ":=")
                expr = self.parse_expression()
                return Assign(ArrayAccess(name, indexes), expr)

            # assignment: x := expr
            if self.match(TokType.OP, ":="):
                self.eat(TokType.OP, ":=")
                expr = self.parse_expression()
                return Assign(name, expr)

            # call: foo(args)
            if self.match(TokType.DELIM, "("):
                args = self.parse_call_args()
                return Call(name, args)

            raise ParseError(7, "Неверный оператор", tok.line, tok.col)

        raise ParseError(7, "Неверный оператор", tok.line, tok.col)

    def parse_if(self) -> If:
        self.eat(TokType.KEYWORD, "if")
        cond = self.parse_expression()
        self.eat(TokType.KEYWORD, "then")
        then_b = self.parse_statement()
        else_b = None
        if self.match(TokType.KEYWORD, "else"):
            self.eat(TokType.KEYWORD, "else")
            else_b = self.parse_statement()
        return If(cond, then_b, else_b)

    def parse_while(self) -> While:
        self.eat(TokType.KEYWORD, "while")
        cond = self.parse_expression()
        self.eat(TokType.KEYWORD, "do")
        body = self.parse_statement()
        return While(cond, body)

    def parse_for(self) -> For:
        self.eat(TokType.KEYWORD, "for")
        var = self.eat(TokType.IDENT).value
        self.eat(TokType.OP, ":=")
        start = self.parse_expression()

        if self.match(TokType.KEYWORD, "to"):
            direction = "to"
            self.eat(TokType.KEYWORD, "to")
        else:
            direction = "downto"
            self.eat(TokType.KEYWORD, "downto")

        end = self.parse_expression()
        self.eat(TokType.KEYWORD, "do")
        body = self.parse_statement()
        return For(var, start, end, direction, body)

    def parse_repeat(self) -> Repeat:
        self.eat(TokType.KEYWORD, "repeat")
        body = []
        while not self.match(TokType.KEYWORD, "until"):
            body.append(self.parse_statement())
            if self.match(TokType.DELIM, ";"):
                self.eat(TokType.DELIM, ";")
        self.eat(TokType.KEYWORD, "until")
        cond = self.parse_expression()
        return Repeat(body, cond)

    def parse_case(self) -> Case:
        self.eat(TokType.KEYWORD, "case")
        expr = self.parse_expression()
        self.eat(TokType.KEYWORD, "of")

        branches = []
        else_branch = None

        while not (self.match(TokType.KEYWORD, "end") or self.match(TokType.KEYWORD, "else")):
            values = [self.parse_expression()]
            while self.match(TokType.DELIM, ","):
                self.eat(TokType.DELIM, ",")
                values.append(self.parse_expression())
            self.eat(TokType.DELIM, ":")
            stmt = self.parse_statement()
            if self.match(TokType.DELIM, ";"):
                self.eat(TokType.DELIM, ";")
            branches.append(CaseBranch(values, stmt))

        if self.match(TokType.KEYWORD, "else"):
            self.eat(TokType.KEYWORD, "else")
            else_branch = self.parse_statement()
            if self.match(TokType.DELIM, ";"):
                self.eat(TokType.DELIM, ";")

        self.eat(TokType.KEYWORD, "end")
        return Case(expr, branches, else_branch)

    def parse_writeln(self) -> Writeln:
        self.eat(TokType.KEYWORD, "writeln")
        args = self.parse_call_args()
        return Writeln(args)

    def parse_readln(self) -> Readln:
        self.eat(TokType.KEYWORD, "readln")
        self.eat(TokType.DELIM, "(")
        names = [self.eat(TokType.IDENT).value]
        while self.match(TokType.DELIM, ","):
            self.eat(TokType.DELIM, ",")
            names.append(self.eat(TokType.IDENT).value)
        self.eat(TokType.DELIM, ")")
        return Readln(names)

    # ======================================================
    # CALL ARGS
    # ======================================================
    def parse_call_args(self) -> List[Expr]:
        args = []
        self.eat(TokType.DELIM, "(")
        if not self.match(TokType.DELIM, ")"):
            args.append(self.parse_expression())
            while self.match(TokType.DELIM, ","):
                self.eat(TokType.DELIM, ",")
                args.append(self.parse_expression())
        self.eat(TokType.DELIM, ")")
        return args

    # ======================================================
    # ARRAY ACCESS
    # ======================================================
    def parse_array_indexes(self) -> List[Expr]:
        indexes = []
        self.eat(TokType.DELIM, "[")
        indexes.append(self.parse_expression())
        while self.match(TokType.DELIM, ","):
            self.eat(TokType.DELIM, ",")
            indexes.append(self.parse_expression())
        self.eat(TokType.DELIM, "]")
        return indexes

    # ======================================================
    # EXPRESSIONS
    # ======================================================
    def parse_expression(self) -> Expr:
        return self.parse_or()

    def parse_or(self) -> Expr:
        node = self.parse_and()
        while self.match(TokType.KEYWORD, "or"):
            op = self.eat(TokType.KEYWORD).value
            node = BinaryOp(op, node, self.parse_and())
        return node

    def parse_and(self) -> Expr:
        node = self.parse_comparison()
        while self.match(TokType.KEYWORD, "and"):
            op = self.eat(TokType.KEYWORD).value
            node = BinaryOp(op, node, self.parse_comparison())
        return node

    def parse_comparison(self) -> Expr:
        node = self.parse_add()
        if self.match(TokType.OP) and self.cur().value in {"=", "<>", "<", ">", "<=", ">="}:
            op = self.eat(TokType.OP).value
            node = BinaryOp(op, node, self.parse_add())
        return node

    def parse_add(self) -> Expr:
        node = self.parse_term()
        while self.match(TokType.OP) and self.cur().value in {"+", "-"}:
            op = self.eat(TokType.OP).value
            node = BinaryOp(op, node, self.parse_term())
        return node

    def parse_term(self) -> Expr:
        node = self.parse_unary()
        while self.match(TokType.OP) and self.cur().value in {"*", "/", "mod"}:
            op = self.eat(TokType.OP).value
            node = BinaryOp(op, node, self.parse_unary())
        return node

    def parse_unary(self) -> Expr:
        if self.match(TokType.KEYWORD, "not"):
            op = self.eat(TokType.KEYWORD).value
            return UnaryOp(op, self.parse_unary())
        if self.match(TokType.OP, "-"):
            op = self.eat(TokType.OP).value
            return UnaryOp(op, self.parse_unary())
        return self.parse_primary()

    def parse_primary(self) -> Expr:
        tok = self.cur()

        if self.match(TokType.INT):
            return Literal(int(self.eat(TokType.INT).value), "integer")

        if self.match(TokType.REAL):
            return Literal(float(self.eat(TokType.REAL).value), "real")

        if self.match(TokType.STRING):
            return Literal(self.eat(TokType.STRING).value, "string")

        if self.match(TokType.CHAR):
            return Literal(self.eat(TokType.CHAR).value, "char")

        if self.match(TokType.BOOL):
            return Literal(self.eat(TokType.BOOL).value == "true", "boolean")

        if self.match(TokType.IDENT):
            name = self.eat(TokType.IDENT).value

            if self.match(TokType.DELIM, "."):
                self.eat(TokType.DELIM, ".")
                fname = self.eat(TokType.IDENT).value
                if self.match(TokType.DELIM, "("):
                    args = self.parse_call_args()
                    if fname == "create":
                        return ObjectCreate(name, args)
                    return MethodCall(name, fname, args)
                return FieldAccess(name, fname)

            if self.match(TokType.DELIM, "["):
                return ArrayAccess(name, self.parse_array_indexes())

            if self.match(TokType.DELIM, "("):
                args = self.parse_call_args()
                return Call(name, args)

            return Identifier(name)

        if self.match(TokType.DELIM, "("):
            self.eat(TokType.DELIM, "(")
            expr = self.parse_expression()
            self.eat(TokType.DELIM, ")")
            return expr

        raise ParseError(7, "Неверный формат выражения", tok.line, tok.col)
