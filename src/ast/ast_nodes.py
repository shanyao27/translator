from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Union


# ================= PROGRAM ===================

@dataclass
class Program:
    name: str
    decls: List["VarDecl"]
    subroutines: List["SubroutineDecl"]
    body: "Block"


# ================= TYPES ===================

@dataclass
class ArrayType:
    ranges: List[tuple[int, int]]  # list of (low, high)
    base_type: str                 # integer, real, char, boolean


@dataclass
class VarDecl:
    names: List[str]
    typ: Union[str, ArrayType]


# ================= SUBROUTINES ===================

class SubroutineDecl:
    pass


@dataclass
class Param:
    name: str
    typ: str


@dataclass
class ProcedureDecl(SubroutineDecl):
    name: str
    params: List[Param]
    body: "Block"


@dataclass
class FunctionDecl(SubroutineDecl):
    name: str
    params: List[Param]
    ret_type: str
    body: "Block"


# ================= STATEMENTS ===================

class Stmt:
    pass


@dataclass
class Block(Stmt):
    statements: List[Stmt]


@dataclass
class Assign(Stmt):
    target: Union[str, "ArrayAccess"]
    expr: "Expr"


@dataclass
class If(Stmt):
    cond: "Expr"
    then_branch: Stmt
    else_branch: Optional[Stmt]


@dataclass
class While(Stmt):
    cond: "Expr"
    body: Stmt


@dataclass
class For(Stmt):
    var: str
    start: "Expr"
    end: "Expr"
    direction: str
    body: Stmt


@dataclass
class Repeat(Stmt):
    body: List[Stmt]
    until_cond: "Expr"


@dataclass
class Writeln(Stmt):
    args: List["Expr"]


@dataclass
class Readln(Stmt):
    args: List[str]


@dataclass
class Call(Stmt):
    name: str
    args: List["Expr"]


# ================= EXPRESSIONS ===================

class Expr:
    pass


@dataclass
class Identifier(Expr):
    name: str


@dataclass
class ArrayAccess(Expr):
    name: str
    indexes: List[Expr]


@dataclass
class Literal(Expr):
    value: Union[int, float, str, bool]
    lit_type: str


@dataclass
class UnaryOp(Expr):
    op: str
    operand: Expr


@dataclass
class BinaryOp(Expr):
    op: str
    left: Expr
    right: Expr
