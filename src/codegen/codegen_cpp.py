# генератор C++ по AST и таблице соответствия
from __future__ import annotations
from src.ast.ast_nodes import *

TYPE_MAP = {
    "integer": "int",
    "real": "float",
    "char": "char",
    "boolean": "bool",
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
        self.lines: List[str] = []

    def emit(self, s: str = ""):
        self.lines.append("    " * self.ind + s)

    def gen(self, prog: Program) -> str:
        self.emit("#include <iostream>")
        self.emit("#include <string>")
        self.emit("")
        self.emit("int main() {")
        self.ind += 1

        # decls
        for d in prog.decls:
            ctyp = TYPE_MAP[d.typ]
            names = ", ".join(d.names)
            self.emit(f"{ctyp} {names};")

        if prog.decls:
            self.emit("")

        self.gen_block(prog.body)

        self.emit("")
        self.emit("return 0;")
        self.ind -= 1
        self.emit("}")
        return "\n".join(self.lines)

    def gen_block(self, b: Block):
        for s in b.statements:
            self.gen_stmt(s)

    def gen_stmt(self, s: Stmt):
        if isinstance(s, Block):
            self.emit("{")
            self.ind += 1
            self.gen_block(s)
            self.ind -= 1
            self.emit("}")
        elif isinstance(s, Assign):
            self.emit(f"{s.target} = {self.gen_expr(s.expr)};")
        elif isinstance(s, If):
            self.emit(f"if ({self.gen_expr(s.cond)})")
            self.gen_stmt(s.then_branch)
            if s.else_branch:
                self.emit("else")
                self.gen_stmt(s.else_branch)
        elif isinstance(s, While):
            self.emit(f"while ({self.gen_expr(s.cond)})")
            self.gen_stmt(s.body)
        elif isinstance(s, For):
            start = self.gen_expr(s.start)
            end = self.gen_expr(s.end)
            if s.direction == "to":
                self.emit(f"for ({s.var} = {start}; {s.var} <= {end}; ++{s.var})")
            else:
                self.emit(f"for ({s.var} = {start}; {s.var} >= {end}; --{s.var})")
            self.gen_stmt(s.body)
        elif isinstance(s, Repeat):
            self.emit("do {")
            self.ind += 1
            for st in s.body:
                self.gen_stmt(st)
            self.ind -= 1
            cond = self.gen_expr(s.until_cond)
            self.emit(f"}} while (!({cond}));")
        elif isinstance(s, Writeln):
            if not s.args:
                self.emit("std::cout << std::endl;")
            else:
                parts = []
                for i, a in enumerate(s.args):
                    if i > 0:
                        parts.append('" "')
                    parts.append(self.gen_expr(a))
                chain = " << ".join(parts)
                self.emit(f"std::cout << {chain} << std::endl;")
        elif isinstance(s, Readln):
            chain = " >> ".join(s.args)
            self.emit(f"std::cin >> {chain};")
        elif isinstance(s, Call):
            args = ", ".join(self.gen_expr(a) for a in s.args)
            self.emit(f"{s.name}({args});")
        else:
            raise RuntimeError(f"Unknown stmt: {s}")

    def gen_expr(self, e: Expr) -> str:
        if isinstance(e, Literal):
            if e.lit_type == "string":
                return '"' + str(e.value) + '"'
            if e.lit_type == "char":
                return "'" + str(e.value) + "'"
            if e.lit_type == "boolean":
                return "true" if e.value else "false"
            return str(e.value)

        if isinstance(e, Identifier):
            return e.name

        if isinstance(e, UnaryOp):
            op = OP_MAP.get(e.op, e.op)
            return f"({op}{self.gen_expr(e.operand)})"

        if isinstance(e, BinaryOp):
            op = OP_MAP.get(e.op, e.op)
            return f"({self.gen_expr(e.left)} {op} {self.gen_expr(e.right)})"

        if isinstance(e, Call):
            args = ", ".join(self.gen_expr(a) for a in e.args)
            return f"{e.name}({args})"

        raise RuntimeError(f"Unknown expr: {e}")
