from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Union


class Stmt:
    pass


class Expr:
    pass


@dataclass
class ArrayType:
    ranges: List[tuple[int, int]]
    base_type: str


@dataclass
class RecordType:
    fields: List["VarDecl"]


@dataclass
class VarDecl:
    names: List[str]
    typ: Union[str, ArrayType, RecordType]


@dataclass
class ConstDecl:
    name: str
    value: "Literal"
    typ: str


@dataclass
class MethodSignature:
    kind: str
    name: str
    params: List["Param"]
    ret_type: Optional[str]


@dataclass
class ClassDecl:
    fields: List["VarDecl"]
    methods: List[MethodSignature]


@dataclass
class TypeDecl:
    name: str
    typ: Union[str, RecordType, ClassDecl]


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


@dataclass
class MethodImpl(SubroutineDecl):
    class_name: str
    method_name: str
    kind: str
    params: List[Param]
    ret_type: Optional[str]
    body: "Block"


@dataclass
class Block(Stmt):
    statements: List[Stmt]


@dataclass
class Assign(Stmt):
    target: Union[str, "ArrayAccess", "FieldAccess"]
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
class Call(Stmt, Expr):
    name: str
    args: List["Expr"]


@dataclass
class MethodCall(Stmt, Expr):
    obj: str
    method: str
    args: List["Expr"]


@dataclass
class ObjectCreate(Expr):
    class_name: str
    args: List["Expr"]


@dataclass
class CaseBranch:
    values: List["Expr"]
    stmt: Stmt


@dataclass
class Case(Stmt):
    expr: "Expr"
    branches: List[CaseBranch]
    else_branch: Optional[Stmt]


@dataclass
class Identifier(Expr):
    name: str


@dataclass
class ArrayAccess(Expr):
    name: str
    indexes: List[Expr]


@dataclass
class FieldAccess(Expr):
    obj: str
    field: str


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


@dataclass
class Program:
    name: str
    const_decls: List[ConstDecl]
    type_decls: List[TypeDecl]
    decls: List[VarDecl]
    subroutines: List[SubroutineDecl]
    body: Block