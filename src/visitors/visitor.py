# src/visitors/visitor.py
from abc import ABC, abstractmethod

class ASTVisitor(ABC):
    """Базовый visitor для обхода AST"""
    
    @abstractmethod
    def visit_program(self, node): pass
    
    @abstractmethod
    def visit_const_decl(self, node): pass
    
    @abstractmethod
    def visit_type_decl(self, node): pass
    
    @abstractmethod
    def visit_var_decl(self, node): pass
    
    @abstractmethod
    def visit_record_type(self, node): pass
    
    @abstractmethod
    def visit_array_type(self, node): pass
    
    @abstractmethod
    def visit_procedure_decl(self, node): pass
    
    @abstractmethod
    def visit_function_decl(self, node): pass
    
    @abstractmethod
    def visit_block(self, node): pass
    
    @abstractmethod
    def visit_assign(self, node): pass
    
    @abstractmethod
    def visit_if(self, node): pass
    
    @abstractmethod
    def visit_while(self, node): pass
    
    @abstractmethod
    def visit_for(self, node): pass
    
    @abstractmethod
    def visit_repeat(self, node): pass
    
    @abstractmethod
    def visit_case(self, node): pass
    
    @abstractmethod
    def visit_writeln(self, node): pass
    
    @abstractmethod
    def visit_readln(self, node): pass
    
    @abstractmethod
    def visit_call(self, node): pass
    
    @abstractmethod
    def visit_literal(self, node): pass
    
    @abstractmethod
    def visit_identifier(self, node): pass
    
    @abstractmethod
    def visit_field_access(self, node): pass
    
    @abstractmethod
    def visit_array_access(self, node): pass
    
    @abstractmethod
    def visit_unary_op(self, node): pass
    
    @abstractmethod
    def visit_binary_op(self, node): pass