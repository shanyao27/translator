from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Union
from abc import ABC, abstractmethod

# ================= BASE CLASSES ===================

class ASTNode(ABC):
    
    @abstractmethod
    def accept(self, visitor):
        pass
    
class Stmt(ASTNode):
    pass

class Expr(ASTNode):
    pass


# ================= TYPES ===================

@dataclass
class ArrayType(ASTNode):
    ranges: List[tuple[int, int]]
    base_type: str
    
    def accept(self, visitor):
        return visitor.visit_array_type(self)

@dataclass
class RecordType(ASTNode):
    fields: List["VarDecl"]
    
    def accept(self, visitor):
        return visitor.visit_record_type(self)

@dataclass
class VarDecl(ASTNode):
    names: List[str]
    typ: Union[str, ArrayType, RecordType]
    
    def accept(self, visitor):
        return visitor.visit_var_decl(self)

# ================= CONST / TYPE DECLS ===================

@dataclass
class ConstDecl(ASTNode):
    name: str
    value: "Literal"
    typ: str
    
    def accept(self, visitor):
        return visitor.visit_const_decl(self)

@dataclass
class MethodSignature:
    kind: str          # 'procedure' | 'function' | 'constructor'
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


# ================= SUBROUTINES ===================

class SubroutineDecl(ASTNode):
    pass

@dataclass
class Param(ASTNode):
    name: str
    typ: str
    
    def accept(self, visitor):
        return visitor.visit_param(self)

@dataclass
class ProcedureDecl(SubroutineDecl):
    name: str
    params: List[Param]
    body: "Block"
    
    def accept(self, visitor):
        return visitor.visit_procedure_decl(self)

@dataclass
class FunctionDecl(SubroutineDecl):
    name: str
    params: List[Param]
    ret_type: str
    body: "Block"
    
    def accept(self, visitor):
        return visitor.visit_function_decl(self)

@dataclass
class MethodImpl(SubroutineDecl):
    class_name: str
    method_name: str
    kind: str          # 'procedure' | 'function' | 'constructor'
    params: List[Param]
    ret_type: Optional[str]
    body: "Block"


# ================= STATEMENTS ===================

@dataclass
class Block(Stmt):
    statements: List[Stmt]
    
    def accept(self, visitor):
        return visitor.visit_block(self)

@dataclass
class Assign(Stmt):
    target: Union[str, "ArrayAccess", "FieldAccess"]
    expr: "Expr"
    
    def accept(self, visitor):
        return visitor.visit_assign(self)

@dataclass
class If(Stmt):
    cond: "Expr"
    then_branch: Stmt
    else_branch: Optional[Stmt]
    
    def accept(self, visitor):
        return visitor.visit_if(self)

@dataclass
class While(Stmt):
    cond: "Expr"
    body: Stmt
    
    def accept(self, visitor):
        return visitor.visit_while(self)

@dataclass
class For(Stmt):
    var: str
    start: "Expr"
    end: "Expr"
    direction: str
    body: Stmt
    
    def accept(self, visitor):
        return visitor.visit_for(self)

@dataclass
class Repeat(Stmt):
    body: List[Stmt]
    until_cond: "Expr"
    
    def accept(self, visitor):
        return visitor.visit_repeat(self)

@dataclass
class Writeln(Stmt):
    args: List["Expr"]
    
    def accept(self, visitor):
        return visitor.visit_writeln(self)

@dataclass
class Readln(Stmt):
    args: List[str]
    
    def accept(self, visitor):
        return visitor.visit_readln(self)

@dataclass
class Call(Stmt, Expr):
    name: str
    args: List["Expr"]
    
    def accept(self, visitor):
        return visitor.visit_call(self)

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
    
    def accept(self, visitor):
        return visitor.visit_case_branch(self)

@dataclass
class Case(Stmt):
    expr: "Expr"
    branches: List[CaseBranch]
    else_branch: Optional[Stmt]
    
    def accept(self, visitor):
        return visitor.visit_case(self)

# ================= EXPRESSIONS ===================

@dataclass
class Identifier(Expr):
    name: str
    
    def accept(self, visitor):
        return visitor.visit_identifier(self)

@dataclass
class ArrayAccess(Expr):
    name: str
    indexes: List[Expr]
    
    def accept(self, visitor):
        return visitor.visit_array_access(self)

@dataclass
class FieldAccess(Expr):
    obj: str
    field: str
    
    def accept(self, visitor):
        return visitor.visit_field_access(self)

@dataclass
class Literal(Expr):
    value: Union[int, float, str, bool]
    lit_type: str
    
    def accept(self, visitor):
        return visitor.visit_literal(self)

@dataclass
class UnaryOp(Expr):
    op: str
    operand: Expr
    
    def accept(self, visitor):
        return visitor.visit_unary_op(self)

@dataclass
class BinaryOp(Expr):
    op: str
    left: Expr
    right: Expr
    
    def accept(self, visitor):
        return visitor.visit_binary_op(self)

# ================= PROGRAM ===================

@dataclass
class Program(ASTNode):
    name: str
    const_decls: List[ConstDecl]
    type_decls: List[TypeDecl]
    decls: List[VarDecl]
    subroutines: List[SubroutineDecl]
    body: Block
    
    def accept(self, visitor):
        return visitor.visit_program(self)