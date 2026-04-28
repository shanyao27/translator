# синтаксический анализатор (recursive descent) -> AST
from __future__ import annotations
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

    # <программа> → program<идентификатор> ;<объявления>begin<операторы>end.
    def parse_program(self) -> Program:
        if not self.match(TokType.KEYWORD, "program"):
            tok = self.cur()
            raise ParseError(0, "Отсутствует заголовок program", tok.line, tok.col)
        self.eat(TokType.KEYWORD, "program")
        name = self.eat(TokType.IDENT).value
        self.eat(TokType.DELIM, ";")
        decls = self.parse_decls()
        if not self.match(TokType.KEYWORD, "begin"):
            tok = self.cur()
            raise ParseError(1, "Ожидалось ключевое слово begin", tok.line, tok.col)
        body = self.parse_block()
        if not self.match(TokType.DELIM, "."):
            tok = self.cur()
            raise ParseError(2, "Программа должна завершаться точкой после end", tok.line, tok.col)
        self.eat(TokType.DELIM, ".")
        self.eat(TokType.EOF)
        return Program(name, decls, body)

    # <объявления> → var<список_объявлений> | ε
    def parse_decls(self) -> List[VarDecl]:
        decls: List[VarDecl] = []
        if self.match(TokType.KEYWORD, "var"):
            self.eat(TokType.KEYWORD, "var")
            while not self.match(TokType.KEYWORD, "begin"):
                decls.append(self.parse_decl())
        return decls

    # <объявление> → <список_переменных> :<тип> ;
    def parse_decl(self) -> VarDecl:
        names = self.parse_id_list()
        self.eat(TokType.DELIM, ":")
        if not (self.match(TokType.KEYWORD) and self.cur().value in TYPE_KEYWORDS):
            tok = self.cur()
            raise ParseError(5, "Ожидался тип данных переменной", tok.line, tok.col)
        typ = self.eat(TokType.KEYWORD).value
        self.eat(TokType.DELIM, ";")
        return VarDecl(names, typ)

    # <список_переменных> → id , <список_переменных> | id
    def parse_id_list(self) -> List[str]:
        ids = [self.eat(TokType.IDENT).value]
        while self.match(TokType.DELIM, ","):
            self.eat(TokType.DELIM, ",")
            ids.append(self.eat(TokType.IDENT).value)
        return ids

    # begin<операторы>end
    def parse_block(self) -> Block:
        self.eat(TokType.KEYWORD, "begin")
        stmts = self.parse_statements(until_kw={"end"})
        self.eat(TokType.KEYWORD, "end")
        return Block(stmts)

    # <операторы> → <оператор> ;<операторы> | <оператор>
    def parse_statements(self, until_kw: set[str]) -> List[Stmt]:
        res: List[Stmt] = []
        while not (self.match(TokType.KEYWORD) and self.cur().value in until_kw):
            res.append(self.parse_statement())
            if self.match(TokType.DELIM, ";"):
                self.eat(TokType.DELIM, ";")
            else:
                # по контексту ; обязателен между операторами
                if not (self.match(TokType.KEYWORD) and self.cur().value in until_kw):
                    tok = self.cur()
                    raise ParseError(3, "Отсутствует точка с запятой после оператора", tok.line, tok.col)
        return res

    # <оператор> → присваивание | условие | цикл | ввод_вывод | begin..end | вызов
    def parse_statement(self) -> Stmt:
        tok = self.cur()

        if self.match(TokType.KEYWORD, "begin"):
            return self.parse_block()
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
            # либо assign, либо call
            name = self.eat(TokType.IDENT).value
            if self.match(TokType.OP, ":="):
                self.eat(TokType.OP, ":=")
                expr = self.parse_expression()
                return Assign(name, expr)
            if self.match(TokType.DELIM, "("):
                args = self.parse_arg_list()
                return Call(name, args)
            raise ParseError(7, "Неверный формат оператора", tok.line, tok.col)

        raise ParseError(7, "Неверный формат оператора", tok.line, tok.col)

    def parse_if(self) -> If:
        self.eat(TokType.KEYWORD, "if")
        cond = self.parse_expression()
        self.eat(TokType.KEYWORD, "then")
        then_branch = self.parse_statement()
        else_branch = None
        if self.match(TokType.KEYWORD, "else"):
            self.eat(TokType.KEYWORD, "else")
            else_branch = self.parse_statement()
        return If(cond, then_branch, else_branch)

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
        elif self.match(TokType.KEYWORD, "downto"):
            direction = "downto"
            self.eat(TokType.KEYWORD, "downto")
        else:
            tok = self.cur()
            raise ParseError(11, "Ожидалось to/downto в for", tok.line, tok.col)
        end = self.parse_expression()
        self.eat(TokType.KEYWORD, "do")
        body = self.parse_statement()
        return For(var, start, end, direction, body)

    def parse_repeat(self) -> Repeat:
        self.eat(TokType.KEYWORD, "repeat")
        body = self.parse_statements(until_kw={"until"})
        self.eat(TokType.KEYWORD, "until")
        cond = self.parse_expression()
        return Repeat(body, cond)

    def parse_writeln(self) -> Writeln:
        self.eat(TokType.KEYWORD, "writeln")
        args = self.parse_arg_list()
        return Writeln(args)

    def parse_readln(self) -> Readln:
        self.eat(TokType.KEYWORD, "readln")
        self.eat(TokType.DELIM, "(")
        ids = [self.eat(TokType.IDENT).value]
        while self.match(TokType.DELIM, ","):
            self.eat(TokType.DELIM, ",")
            ids.append(self.eat(TokType.IDENT).value)
        self.eat(TokType.DELIM, ")")
        return Readln(ids)

    def parse_arg_list(self) -> List[Expr]:
        self.eat(TokType.DELIM, "(")
        args: List[Expr] = []
        if not self.match(TokType.DELIM, ")"):
            args.append(self.parse_expression())
            while self.match(TokType.DELIM, ","):
                self.eat(TokType.DELIM, ",")
                args.append(self.parse_expression())
        self.eat(TokType.DELIM, ")")
        return args

    # ======= EXPRESSIONS (приоритеты) =======

    def parse_expression(self) -> Expr:
        return self.parse_or()

    def parse_or(self) -> Expr:
        node = self.parse_and()
        while self.match(TokType.KEYWORD, "or"):
            op = self.eat(TokType.KEYWORD).value
            right = self.parse_and()
            node = BinaryOp(op, node, right)
        return node

    def parse_and(self) -> Expr:
        node = self.parse_comparison()
        while self.match(TokType.KEYWORD, "and"):
            op = self.eat(TokType.KEYWORD).value
            right = self.parse_comparison()
            node = BinaryOp(op, node, right)
        return node

    def parse_comparison(self) -> Expr:
        node = self.parse_add()
        if self.match(TokType.OP) and self.cur().value in {"=", "<>", "<", ">", "<=", ">="}:
            op = self.eat(TokType.OP).value
            right = self.parse_add()
            node = BinaryOp(op, node, right)
        return node

    def parse_add(self) -> Expr:
        node = self.parse_term()
        while self.match(TokType.OP) and self.cur().value in {"+", "-"}:
            op = self.eat(TokType.OP).value
            right = self.parse_term()
            node = BinaryOp(op, node, right)
        return node

    def parse_term(self) -> Expr:
        node = self.parse_unary()
        while (self.match(TokType.OP) and self.cur().value in {"*", "/", "mod"}):
            op = self.eat(TokType.OP).value
            right = self.parse_unary()
            node = BinaryOp(op, node, right)
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
            v = int(self.eat(TokType.INT).value)
            return Literal(v, "integer")
        if self.match(TokType.REAL):
            v = float(self.eat(TokType.REAL).value)
            return Literal(v, "real")
        if self.match(TokType.STRING):
            s = self.eat(TokType.STRING).value
            return Literal(s, "string")
        if self.match(TokType.CHAR):
            c = self.eat(TokType.CHAR).value
            return Literal(c, "char")
        if self.match(TokType.BOOL):
            b = self.eat(TokType.BOOL).value == "true"
            return Literal(b, "boolean")

        if self.match(TokType.IDENT):
            name = self.eat(TokType.IDENT).value
            if self.match(TokType.DELIM, "("):
                args = self.parse_arg_list()
                return Call(name, args)  # Call как Expr тоже ок (функции)
            return Identifier(name)

        if self.match(TokType.DELIM, "("):
            self.eat(TokType.DELIM, "(")
            node = self.parse_expression()
            self.eat(TokType.DELIM, ")")
            return node

        raise ParseError(7, "Неверный формат выражения", tok.line, tok.col)
