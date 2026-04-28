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


    def parse_program(self) -> Program:
        self.eat(TokType.KEYWORD, "program")
        name = self.eat(TokType.IDENT).value
        self.eat(TokType.DELIM, ";")

        const_decls = self.parse_consts()
        type_decls = self.parse_type_decls()
        decls = self.parse_decls()
        subs = self.parse_subroutines()

        decls += self.parse_decls()

        self.eat(TokType.KEYWORD, "begin")
        body = self.parse_block_body()
        self.eat(TokType.KEYWORD, "end")
        self.eat(TokType.DELIM, ".")
        self.eat(TokType.EOF)

        return Program(name, const_decls, type_decls, decls, subs, body)


    def parse_consts(self) -> List[ConstDecl]:
        consts = []
        if not self.match(TokType.KEYWORD, "const"):
            return consts
        self.eat(TokType.KEYWORD, "const")
        _stop = {"type", "var", "procedure", "function"}
        while True:
            tok_name = self.cur()
            if self.match(TokType.KEYWORD):

                if tok_name.value == "begin":

                    saved_i = self.i
                    self.i += 1
                    if self.match(TokType.OP, "="):
                        self.i = saved_i
                        raise ParseError(7, "Использование зарезервированного слова в качестве имени константы", tok_name.line, tok_name.col)
                    self.i = saved_i
                    break
                if tok_name.value in _stop:
                    break
                raise ParseError(7, "Использование зарезервированного слова в качестве имени константы", tok_name.line, tok_name.col)
            if not self.match(TokType.IDENT):
                break
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
                    raise ParseError(5, "Недопустимый символ в выражении", tok.line, tok.col)
                val = Literal(self.eat(TokType.STRING).value, "string")
            elif tok.type == TokType.CHAR:
                if neg:
                    raise ParseError(5, "Недопустимый символ в выражении", tok.line, tok.col)
                val = Literal(self.eat(TokType.CHAR).value, "char")
            elif tok.type == TokType.BOOL:
                if neg:
                    raise ParseError(5, "Недопустимый символ в выражении", tok.line, tok.col)
                val = Literal(self.eat(TokType.BOOL).value == "true", "boolean")
            else:
                raise ParseError(5, "Ожидалась константа", tok.line, tok.col)

            self.eat(TokType.DELIM, ";")
            consts.append(ConstDecl(name, val, val.lit_type))
        return consts


    def parse_type_decls(self) -> List[TypeDecl]:
        type_decls = []
        while self.match(TokType.KEYWORD, "type"):
            self.eat(TokType.KEYWORD, "type")
            while self.match(TokType.IDENT) or (not self.match(TokType.KEYWORD, "var")
                    and not self.match(TokType.KEYWORD, "begin")
                    and not self.match(TokType.KEYWORD, "procedure")
                    and not self.match(TokType.KEYWORD, "function")
                    and not self.match(TokType.KEYWORD, "constructor")
                    and not self.match(TokType.KEYWORD, "type")
                    and not self.match(TokType.EOF)):
                tok = self.cur()
                if not self.match(TokType.IDENT):
                    raise ParseError(7, "Ожидалось имя типа", tok.line, tok.col)
                name = self.eat(TokType.IDENT).value
                tok_eq = self.cur()
                if not self.match(TokType.OP, "="):
                    raise ParseError(7, "Ожидалось \"=\"", tok_eq.line, tok_eq.col)
                self.eat(TokType.OP, "=")
                if self.match(TokType.KEYWORD, "record"):
                    typ = self.parse_record_type()
                elif self.match(TokType.KEYWORD, "class"):
                    typ = self.parse_class_type()
                else:
                    tok_rec = self.cur()
                    raise ParseError(7, "Ожидалось \"record\"", tok_rec.line, tok_rec.col)
                self.eat(TokType.DELIM, ";")
                type_decls.append(TypeDecl(name, typ))
        return type_decls

    def parse_class_type(self) -> "ClassDecl":
        self.eat(TokType.KEYWORD, "class")
        fields = []
        methods = []
        seen_methods = set()
        while not self.match(TokType.KEYWORD, "end"):

            if self.match(TokType.EOF) or self.match(TokType.KEYWORD, "begin"):
                raise ParseError(3, "Ожидалось \"end\"", self.cur().line, self.cur().col)
            if self.match(TokType.KEYWORD, "constructor"):
                self.eat(TokType.KEYWORD, "constructor")

                tok_id = self.cur()
                if not self.match(TokType.IDENT):
                    raise ParseError(7, "Ожидался идентификатор конструктора", tok_id.line, tok_id.col)
                name = self.eat(TokType.IDENT).value
                params = self.parse_param_list_opt()
                self.eat(TokType.DELIM, ";")
                methods.append(MethodSignature("constructor", name, params, None))
            elif self.match(TokType.KEYWORD, "procedure"):
                self.eat(TokType.KEYWORD, "procedure")
                name = self.eat(TokType.IDENT).value

                if name in seen_methods:
                    raise ParseError(7, "Повторное объявление метода", self.cur().line, self.cur().col)
                seen_methods.add(name)
                params = self.parse_param_list_opt()
                self.eat(TokType.DELIM, ";")
                methods.append(MethodSignature("procedure", name, params, None))
            elif self.match(TokType.KEYWORD, "function"):
                self.eat(TokType.KEYWORD, "function")
                name = self.eat(TokType.IDENT).value
                if name in seen_methods:
                    raise ParseError(7, "Повторное объявление метода", self.cur().line, self.cur().col)
                seen_methods.add(name)
                params = self.parse_param_list_opt()
                self.eat(TokType.DELIM, ":")
                ret_type = self.eat(TokType.KEYWORD).value
                self.eat(TokType.DELIM, ";")
                methods.append(MethodSignature("function", name, params, ret_type))
            else:
                fields.append(self.parse_decl())

        if not fields and not methods:
            raise ParseError(5, "Пустой класс", self.cur().line, self.cur().col)
        self.eat(TokType.KEYWORD, "end")
        return ClassDecl(fields, methods)

    def parse_record_type(self) -> RecordType:
        self.eat(TokType.KEYWORD, "record")
        fields = []
        while not self.match(TokType.KEYWORD, "end"):
            if self.match(TokType.EOF) or self.match(TokType.KEYWORD, "begin"):
                raise ParseError(3, "Ожидалось \"end\"", self.cur().line, self.cur().col)
            fields.append(self.parse_decl())
        if not fields:
            raise ParseError(5, "Пустой record", self.cur().line, self.cur().col)
        self.eat(TokType.KEYWORD, "end")
        return RecordType(fields)


    def parse_decls(self) -> List[VarDecl]:
        decls = []
        if self.match(TokType.KEYWORD, "var"):
            self.eat(TokType.KEYWORD, "var")
            while True:

                if self.match(TokType.KEYWORD):
                    kw = self.cur().value

                    if kw in {"begin", "procedure", "function", "constructor"}:

                        saved = self.i
                        self.i += 1
                        next_is_colon = self.match(TokType.DELIM, ":")
                        self.i = saved
                        if not next_is_colon:
                            break

                    tok = self.cur()
                    raise ParseError(7, "Использование зарезервированного слова в качестве имени переменной", tok.line, tok.col)
                if self.match(TokType.EOF):
                    break
                decls.append(self.parse_decl())
        return decls

    def parse_decl(self) -> VarDecl:
        names = self.parse_id_list()
        tok = self.cur()
        if not self.match(TokType.DELIM, ":"):
            raise ParseError(7, "Ожидалось \":\"", tok.line, tok.col)
        self.eat(TokType.DELIM, ":")
        typ = self.parse_type()
        tok2 = self.cur()
        if not self.match(TokType.DELIM, ";"):
            raise ParseError(7, "Ожидалось \";\"", tok2.line, tok2.col)
        self.eat(TokType.DELIM, ";")
        return VarDecl(names, typ)

    def parse_id_list(self) -> List[str]:
        tok = self.cur()
        if tok.type == TokType.INT:
            raise ParseError(7, "Идентификатор начинается с цифры", tok.line, tok.col)
        if tok.type == TokType.KEYWORD:
            raise ParseError(7, "Использование зарезервированного слова в качестве имени переменной", tok.line, tok.col)
        ids = [self.eat(TokType.IDENT).value]
        while self.match(TokType.DELIM, ","):
            self.eat(TokType.DELIM, ",")
            ids.append(self.eat(TokType.IDENT).value)
        return ids


    def parse_type(self):

        if self.match(TokType.DELIM, "["):
            raise ParseError(7, "Ожидалось array", self.cur().line, self.cur().col)

        if self.match(TokType.KEYWORD, "array"):
            self.eat(TokType.KEYWORD, "array")

            tok_br = self.cur()
            if not self.match(TokType.DELIM, "["):
                raise ParseError(7, "Ожидалось \"[\"", tok_br.line, tok_br.col)
            self.eat(TokType.DELIM, "[")
            ranges = []

            while True:
                low = int(self.eat(TokType.INT).value)
                self.eat(TokType.OP, "..")
                high = int(self.eat(TokType.INT).value)

                if low > high:
                    raise ParseError(5, "Неверный диапазон", self.cur().line, self.cur().col)
                ranges.append((low, high))
                if self.match(TokType.DELIM, ","):
                    self.eat(TokType.DELIM, ",")
                else:
                    break

            self.eat(TokType.DELIM, "]")

            tok_of = self.cur()
            if not self.match(TokType.KEYWORD, "of"):
                raise ParseError(7, "Ожидалось \"of\"", tok_of.line, tok_of.col)
            self.eat(TokType.KEYWORD, "of")


            if not (self.match(TokType.KEYWORD) and self.cur().value in TYPE_KEYWORDS):
                raise ParseError(5, "Ожидался тип элементов")
            base = self.eat(TokType.KEYWORD).value
            return ArrayType(ranges, base)


        if self.match(TokType.IDENT):
            return self.eat(TokType.IDENT).value

        if not (self.match(TokType.KEYWORD) and self.cur().value in TYPE_KEYWORDS):
            raise ParseError(5, "Ожидался тип данных")
        return self.eat(TokType.KEYWORD).value


    def parse_subroutines(self) -> List[SubroutineDecl]:
        subs = []
        while (self.match(TokType.KEYWORD, "procedure")
               or self.match(TokType.KEYWORD, "function")
               or self.match(TokType.KEYWORD, "constructor")):
            kind = self.eat(TokType.KEYWORD).value

            tok_name = self.cur()
            if not self.match(TokType.IDENT):
                raise ParseError(7, "Ожидался идентификатор", tok_name.line, tok_name.col)
            name = self.eat(TokType.IDENT).value

            if self.match(TokType.DELIM, "."):
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

                tok_begin = self.cur()
                if not self.match(TokType.KEYWORD, "begin"):
                    raise ParseError(7, "Ожидалось \"begin\"", tok_begin.line, tok_begin.col)
                self.eat(TokType.KEYWORD, "begin")
                body = self.parse_block_body()
                self.eat(TokType.KEYWORD, "end")
                self.eat(TokType.DELIM, ";")
                subs.append(ProcedureDecl(name, params, body))
            elif kind == "function":
                params = self.parse_param_list_opt()

                tok_colon = self.cur()
                if not self.match(TokType.DELIM, ":"):
                    raise ParseError(7, "Ожидался тип возвращаемого значения", tok_colon.line, tok_colon.col)
                self.eat(TokType.DELIM, ":")
                ret_type = self.eat(TokType.KEYWORD).value
                self.eat(TokType.DELIM, ";")
                tok_begin = self.cur()
                if not self.match(TokType.KEYWORD, "begin"):
                    raise ParseError(7, "Ожидалось \"begin\"", tok_begin.line, tok_begin.col)
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
            while not self.match(TokType.DELIM, ")"):
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


    def parse_block_body(self) -> Block:
        stmts = []
        while not self.match(TokType.KEYWORD, "end"):

            if self.match(TokType.EOF) or self.match(TokType.DELIM, "."):
                raise ParseError(3, "Ожидалось \"end\"", self.cur().line, self.cur().col)
            if self.match(TokType.DELIM, ")"):
                raise ParseError(7, "Лишняя скобка", self.cur().line, self.cur().col)
            stmts.append(self.parse_statement())
            if self.match(TokType.DELIM, ";"):
                self.eat(TokType.DELIM, ";")
            else:
                if not self.match(TokType.KEYWORD, "end"):
                    if self.match(TokType.EOF) or self.match(TokType.DELIM, "."):
                        raise ParseError(3, "Ожидалось \"end\"", self.cur().line, self.cur().col)
                    if self.match(TokType.DELIM, ")"):
                        raise ParseError(7, "Лишняя скобка", self.cur().line, self.cur().col)
                    raise ParseError(3, "Пропущен ;")
        return Block(stmts)
        return Block(stmts)

    def parse_block_body_inner(self) -> Block:
        stmts = []
        while not self.match(TokType.KEYWORD, "end") and not self.match(TokType.EOF) and not self.match(TokType.DELIM, "."):
            stmts.append(self.parse_statement())
            if self.match(TokType.DELIM, ";"):
                self.eat(TokType.DELIM, ";")
            else:
                if not self.match(TokType.KEYWORD, "end"):
                    break
        return Block(stmts)


    def parse_statement(self) -> Stmt:
        tok = self.cur()

        if self.match(TokType.KEYWORD, "begin"):
            self.eat(TokType.KEYWORD, "begin")
            body = self.parse_block_body_inner()
            if not self.match(TokType.KEYWORD, "end"):
                raise ParseError(3, "Ожидалось \"end\"", self.cur().line, self.cur().col)
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


            if self.match(TokType.OP, "->"):
                self.eat(TokType.OP, "->")
                fname = self.eat(TokType.IDENT).value
                if self.match(TokType.DELIM, "("):
                    args = self.parse_call_args()
                    return MethodCall(name, fname, args)
                if self.match(TokType.OP, ":="):
                    self.eat(TokType.OP, ":=")
                    expr = self.parse_expression()
                    return Assign(FieldAccess(name, fname), expr)
                return MethodCall(name, fname, [])


            if self.match(TokType.DELIM, "."):
                self.eat(TokType.DELIM, ".")
                fname = self.eat(TokType.IDENT).value
                if self.match(TokType.DELIM, "("):
                    args = self.parse_call_args()
                    return MethodCall(name, fname, args)
                if self.match(TokType.OP, ":="):
                    self.eat(TokType.OP, ":=")
                    expr = self.parse_expression()
                    return Assign(FieldAccess(name, fname), expr)
                return MethodCall(name, fname, [])


            if self.match(TokType.DELIM, "["):
                indexes = self.parse_array_indexes()
                self.eat(TokType.OP, ":=")
                expr = self.parse_expression()
                return Assign(ArrayAccess(name, indexes), expr)


            if self.match(TokType.OP, ":="):
                self.eat(TokType.OP, ":=")
                expr = self.parse_expression()
                return Assign(name, expr)


            if self.match(TokType.DELIM, "("):
                args = self.parse_call_args()
                return Call(name, args)

            raise ParseError(7, "Неверный оператор", tok.line, tok.col)

        if self.match(TokType.DELIM, ")"):
            raise ParseError(7, "Лишняя скобка", tok.line, tok.col)

        raise ParseError(7, "Неверный оператор", tok.line, tok.col)

    def parse_if(self) -> If:
        self.eat(TokType.KEYWORD, "if")
        tok = self.cur()

        if self.match(TokType.KEYWORD, "then"):
            raise ParseError(7, "Ожидалось условие", tok.line, tok.col)
        cond = self.parse_expression()

        if self.match(TokType.DELIM, ";"):
            raise ParseError(7, "Неожиданный символ ;", self.cur().line, self.cur().col)
        if not self.match(TokType.KEYWORD, "then"):
            raise ParseError(7, "Ожидалось \"then\"", self.cur().line, self.cur().col)
        self.eat(TokType.KEYWORD, "then")
        tok_then = self.cur()

        if self.match(TokType.KEYWORD, "end") or self.match(TokType.KEYWORD, "else") or self.match(TokType.EOF):
            raise ParseError(7, "Ожидалась ветка после \"then\"", tok_then.line, tok_then.col)
        then_b = self.parse_statement()
        else_b = None

        if self.match(TokType.DELIM, ";"):

            saved_i = self.i
            self.i += 1
            if self.match(TokType.KEYWORD, "else"):
                raise ParseError(7, "Неожиданный символ ;", self.toks[saved_i].line, self.toks[saved_i].col)
            self.i = saved_i
        if self.match(TokType.KEYWORD, "else"):
            self.eat(TokType.KEYWORD, "else")
            tok_else = self.cur()

            if self.match(TokType.DELIM, ";") or self.match(TokType.KEYWORD, "end") or self.match(TokType.EOF):
                raise ParseError(7, "Ожидалась ветка после \"else\"", tok_else.line, tok_else.col)
            else_b = self.parse_statement()
        return If(cond, then_b, else_b)

    def parse_while(self) -> While:
        self.eat(TokType.KEYWORD, "while")
        tok = self.cur()
        if self.match(TokType.KEYWORD, "do"):
            raise ParseError(7, "Ожидалось выражение", tok.line, tok.col)
        cond = self.parse_expression()
        tok_do = self.cur()
        if not self.match(TokType.KEYWORD, "do"):
            raise ParseError(7, "Ожидалось \"do\"", tok_do.line, tok_do.col)
        self.eat(TokType.KEYWORD, "do")
        tok_body = self.cur()
        if self.match(TokType.DELIM, ";") or self.match(TokType.KEYWORD, "end") or self.match(TokType.EOF):
            raise ParseError(7, "Пустое тело цикла", tok_body.line, tok_body.col)
        body = self.parse_statement()
        return While(cond, body)

    def parse_for(self) -> For:
        self.eat(TokType.KEYWORD, "for")
        var = self.eat(TokType.IDENT).value
        tok = self.cur()
        if not self.match(TokType.OP, ":="):
            raise ParseError(7, "Ожидалось \":=\"", tok.line, tok.col)
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
            raise ParseError(7, "Ожидалось \"to\" или \"downto\"", tok.line, tok.col)

        end = self.parse_expression()
        tok_do = self.cur()
        if not self.match(TokType.KEYWORD, "do"):
            raise ParseError(7, "Ожидалось \"do\"", tok_do.line, tok_do.col)
        self.eat(TokType.KEYWORD, "do")
        tok_body = self.cur()
        if self.match(TokType.KEYWORD, "end") or self.match(TokType.EOF) or self.match(TokType.DELIM, ";"):
            raise ParseError(7, "Пустое тело цикла", tok_body.line, tok_body.col)
        body = self.parse_statement()
        return For(var, start, end, direction, body)

    def parse_repeat(self) -> Repeat:
        self.eat(TokType.KEYWORD, "repeat")
        body = []
        while not self.match(TokType.KEYWORD, "until"):
            if self.match(TokType.EOF) or self.match(TokType.KEYWORD, "end"):
                raise ParseError(7, "Ожидалось until", self.cur().line, self.cur().col)
            body.append(self.parse_statement())
            if self.match(TokType.DELIM, ";"):
                self.eat(TokType.DELIM, ";")
        if not body:
            raise ParseError(7, "Пустое тело цикла", self.cur().line, self.cur().col)
        self.eat(TokType.KEYWORD, "until")
        tok = self.cur()
        if self.match(TokType.DELIM, ";") or self.match(TokType.KEYWORD, "end") or self.match(TokType.EOF):
            raise ParseError(7, "Ожидалось выражение", tok.line, tok.col)
        cond = self.parse_expression()
        return Repeat(body, cond)

    def parse_case(self) -> Case:
        self.eat(TokType.KEYWORD, "case")
        expr = self.parse_expression()

        tok_of = self.cur()
        if not self.match(TokType.KEYWORD, "of"):
            raise ParseError(7, "Ожидалось \"of\"", tok_of.line, tok_of.col)
        self.eat(TokType.KEYWORD, "of")

        branches = []
        else_branch = None
        else_seen = False
        seen_labels = set()


        if self.match(TokType.KEYWORD, "end"):
            raise ParseError(7, "Оператор case должен содержать хотя бы одну ветку", self.cur().line, self.cur().col)

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
            if self.match(TokType.KEYWORD, "else"):
                raise ParseError(7, "Повторное объявление ветки \"else\"", self.cur().line, self.cur().col)


        if not self.match(TokType.KEYWORD, "end"):
            raise ParseError(3, "Ожидалось \"end\"", self.cur().line, self.cur().col)
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


    def parse_array_indexes(self) -> List[Expr]:
        indexes = []
        self.eat(TokType.DELIM, "[")
        indexes.append(self.parse_expression())
        while self.match(TokType.DELIM, ","):
            self.eat(TokType.DELIM, ",")
            indexes.append(self.parse_expression())
        self.eat(TokType.DELIM, "]")
        return indexes


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
        while True:
            if self.match(TokType.OP) and self.cur().value in {"*", "/"}:
                op = self.eat(TokType.OP).value
            elif self.match(TokType.KEYWORD, "mod"):
                op = self.eat(TokType.KEYWORD).value
            else:
                break
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
            if not self.match(TokType.DELIM, ")"):
                raise ParseError(7, "Несбалансированные скобки", self.cur().line, self.cur().col)
            self.eat(TokType.DELIM, ")")
            return expr

        raise ParseError(7, "Ожидалось выражение", tok.line, tok.col)