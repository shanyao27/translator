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

        decls = self.parse_decls()
        subs = self.parse_subroutines()

        self.eat(TokType.KEYWORD, "begin")
        body = self.parse_block_body()
        self.eat(TokType.KEYWORD, "end")
        self.eat(TokType.DELIM, ".")
        self.eat(TokType.EOF)

        return Program(name, decls, subs, body)

    # ======================================================
    # DECLARATIONS (var ...)
    # ======================================================
    def parse_decls(self) -> List[VarDecl]:
        decls = []
        if self.match(TokType.KEYWORD, "var"):
            self.eat(TokType.KEYWORD, "var")
            while not (self.match(TokType.KEYWORD, "begin")
                       or self.match(TokType.KEYWORD, "procedure")
                       or self.match(TokType.KEYWORD, "function")):
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
    # TYPE PARSER (simple + array)
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

        if not (self.match(TokType.KEYWORD) and self.cur().value in TYPE_KEYWORDS):
            raise ParseError(5, "Ожидался тип переменной")
        return self.eat(TokType.KEYWORD).value

    # ======================================================
    # SUBROUTINES
    # ======================================================
    def parse_subroutines(self) -> List[SubroutineDecl]:
        subs = []
        while self.match(TokType.KEYWORD, "procedure") or self.match(TokType.KEYWORD, "function"):
            if self.match(TokType.KEYWORD, "procedure"):
                subs.append(self.parse_procedure())
            else:
                subs.append(self.parse_function())
        return subs

    def parse_procedure(self) -> ProcedureDecl:
        self.eat(TokType.KEYWORD, "procedure")
        name = self.eat(TokType.IDENT).value
        params = self.parse_param_list_opt()
        self.eat(TokType.DELIM, ";")

        self.eat(TokType.KEYWORD, "begin")
        body = self.parse_block_body()
        self.eat(TokType.KEYWORD, "end")
        self.eat(TokType.DELIM, ";")

        return ProcedureDecl(name, params, body)

    def parse_function(self) -> FunctionDecl:
        self.eat(TokType.KEYWORD, "function")
        name = self.eat(TokType.IDENT).value
        params = self.parse_param_list_opt()
        self.eat(TokType.DELIM, ":")
        ret_type = self.eat(TokType.KEYWORD).value
        self.eat(TokType.DELIM, ";")

        self.eat(TokType.KEYWORD, "begin")
        body = self.parse_block_body()
        self.eat(TokType.KEYWORD, "end")
        self.eat(TokType.DELIM, ";")

        return FunctionDecl(name, params, ret_type, body)

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

        if self.match(TokType.KEYWORD, "writeln"):
            return self.parse_writeln()

        if self.match(TokType.KEYWORD, "readln"):
            return self.parse_readln()

        if self.match(TokType.IDENT):
            name = self.eat(TokType.IDENT).value

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

            # call: foo(expr)
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
