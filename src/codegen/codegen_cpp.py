from __future__ import annotations
from src.ast.ast_nodes import *

TYPE_MAP = {
    "integer": "int",
    "real": "float",
    "char": "char",
    "boolean": "bool",
    "string": "std::string",
}

OP_MAP = {
    ":=": "=",
    "mod": "%",
    "and": "&&",
    "or": "||",
    "not": "!",
    "=": "==",
    "<>": "!=",
}


class CppGenerator:
    def __init__(self):
        self.ind = 0
        self.lines = []
        self.current_function = None     # для return через fname := value

    # -------------------------
    def emit(self, s=""):
        self.lines.append("    " * self.ind + s)

    # -------------------------
    def gen(self, prog: Program) -> str:

        self.emit("#include <iostream>")
        self.emit("#include <string>")
        self.emit("")

        # процедуры и функции до main
        for sub in prog.subroutines:
            self.gen_subroutine(sub)
            self.emit("")

        # MAIN
        self.emit("int main() {")
        self.ind += 1

        # глобальные переменные
        for d in prog.decls:
            self.gen_decl(d)
        if prog.decls:
            self.emit("")

        self.gen_block(prog.body, wrap=False)

        self.emit("return 0;")
        self.ind -= 1
        self.emit("}")

        return "\n".join(self.lines)

    # -------------------------
    def gen_decl(self, d: VarDecl):
        typ = d.typ
        if isinstance(typ, str):
            ctyp = TYPE_MAP[typ]
            names = ", ".join(d.names)
            self.emit(f"{ctyp} {names};")
            return

        if isinstance(typ, ArrayType):
            base = TYPE_MAP[typ.base_type]
            dims = "".join(f"[{h - l + 1}]" for (l, h) in typ.ranges)
            for n in d.names:
                self.emit(f"{base} {n}{dims};")

    # -------------------------
    def gen_subroutine(self, sub):
        if isinstance(sub, ProcedureDecl):
            params = ", ".join(self.gen_param(p) for p in sub.params)
            self.emit(f"void {sub.name}({params}) {{")
            self.ind += 1
            self.gen_block(sub.body, wrap=False)
            self.ind -= 1
            self.emit("}")
            return

        if isinstance(sub, FunctionDecl):
            ret = TYPE_MAP[sub.ret_type]
            params = ", ".join(self.gen_param(p) for p in sub.params)
            self.emit(f"{ret} {sub.name}({params}) {{")

            self.ind += 1
            saved = self.current_function
            self.current_function = sub.name
            self.gen_block(sub.body, wrap=False)
            self.current_function = saved
            self.ind -= 1

            self.emit("}")
            return

    # -------------------------
    def gen_param(self, p: Param):
        return f"{TYPE_MAP[p.typ]} {p.name}"

    # -------------------------
    def gen_block(self, b: Block, wrap=False):
        if wrap:
            self.emit("{")
            self.ind += 1

        for s in b.statements:
            self.gen_stmt(s)

        if wrap:
            self.ind -= 1
            self.emit("}")

    # -------------------------
    def gen_stmt(self, s: Stmt):

        if isinstance(s, Block):
            self.gen_block(s)
            return

        if isinstance(s, Assign):

            # return через fname := expr
            if isinstance(s.target, str) and s.target == self.current_function:
                self.emit(f"return {self.gen_expr(s.expr)};")
                return

            left = self.gen_assign_left(s.target)
            self.emit(f"{left} = {self.gen_expr(s.expr)};")
            return

        if isinstance(s, If):
            cond = self.gen_expr(s.cond)
            self.emit(f"if ({cond}) {{")
            self.ind += 1
            self.gen_stmt(s.then_branch)
            self.ind -= 1
            self.emit("}")
            if s.else_branch is not None:
                self.emit("else {")
                self.ind += 1
                self.gen_stmt(s.else_branch)
                self.ind -= 1
                self.emit("}")
            return

        if isinstance(s, While):
            cond = self.gen_expr(s.cond)
            self.emit(f"while ({cond}) {{")
            self.ind += 1
            self.gen_stmt(s.body)
            self.ind -= 1
            self.emit("}")
            return

        if isinstance(s, For):
            start = self.gen_expr(s.start)
            end = self.gen_expr(s.end)
            if s.direction == "to":
                cond = f"{s.var} <= {end}"
                inc = f"++{s.var}"
            else:
                cond = f"{s.var} >= {end}"
                inc = f"--{s.var}"

            self.emit(f"for ({s.var} = {start}; {cond}; {inc}) {{")
            self.ind += 1
            self.gen_stmt(s.body)
            self.ind -= 1
            self.emit("}")
            return

        if isinstance(s, Repeat):
            self.emit("do {")
            self.ind += 1
            for st in s.body:
                self.gen_stmt(st)
            self.ind -= 1
            cond = self.gen_expr(s.until_cond)
            self.emit(f"}} while (!({cond}));")
            return

        if isinstance(s, Writeln):
            if not s.args:
                self.emit("std::cout << std::endl;")
            else:
                parts = []
                for i, a in enumerate(s.args):
                    if i > 0:
                        parts.append('" "')
                    parts.append(self.gen_expr(a))
                self.emit(f"std::cout << {' << '.join(parts)} << std::endl;")
            return

        if isinstance(s, Readln):
            chain = " >> ".join(s.args)
            self.emit(f"std::cin >> {chain};")
            return

        if isinstance(s, Call):
            args = ", ".join(self.gen_expr(a) for a in s.args)
            self.emit(f"{s.name}({args});")
            return

        raise RuntimeError("Unknown statement")

    # -------------------------
    def gen_assign_left(self, target):
        if isinstance(target, str):
            return target
        if isinstance(target, ArrayAccess):
            idx = "".join(f"[{self.gen_expr(i)}]" for i in target.indexes)
            return f"{target.name}{idx}"
        raise RuntimeError("Invalid assignment target")

    # -------------------------
    def gen_expr(self, e: Expr):
        if isinstance(e, Literal):
            if e.lit_type == "string":
                return f"\"{e.value}\""
            if e.lit_type == "char":
                return f"'{e.value}'"
            if e.lit_type == "boolean":
                return "true" if e.value else "false"
            return str(e.value)

        if isinstance(e, Identifier):
            return e.name

        if isinstance(e, ArrayAccess):
            idx = "".join(f"[{self.gen_expr(i)}]" for i in e.indexes)
            return f"{e.name}{idx}"

        if isinstance(e, UnaryOp):
            op = OP_MAP.get(e.op, e.op)
            return f"({op}{self.gen_expr(e.operand)})"

        if isinstance(e, BinaryOp):
            op = OP_MAP.get(e.op, e.op)
            return f"({self.gen_expr(e.left)} {op} {self.gen_expr(e.right)})"

        if isinstance(e, Call):
            args = ", ".join(self.gen_expr(a) for a in e.args)
            return f"{e.name}({args})"

        raise RuntimeError("Unknown expression")
