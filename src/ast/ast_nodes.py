# классы узлов AST (Program, VarDecl, Assign, If, While, For, Repeat, Call, Expr...)
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Union

# ==== Program / Decls ====

@dataclass
class Program:
    name: str
    decls: List["VarDecl"]
    body: "Block"

@dataclass
class VarDecl:
    names: List[str]
    typ: str  # 'integer' | 'real' | 'char' | 'boolean'

# ==== Statements ====

class Stmt: ...

@dataclass
class Block(Stmt):
    statements: List[Stmt]

@dataclass
class Assign(Stmt):
    target: str
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
    direction: str  # 'to' | 'downto'
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

# ==== Expressions ====

class Expr: ...

@dataclass
class Identifier(Expr):
    name: str

@dataclass
class Literal(Expr):
    value: Union[int, float, str, bool]
    lit_type: str  # 'integer'|'real'|'char'|'string'|'boolean'

@dataclass
class UnaryOp(Expr):
    op: str
    operand: Expr

@dataclass
class BinaryOp(Expr):
    op: str
    left: Expr
    right: Expr
