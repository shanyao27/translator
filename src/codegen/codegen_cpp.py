from src.visitors.visitor import ASTVisitor
from src.ast.ast_nodes import *
from typing import Union, List


class CppGenerator(ASTVisitor):
    def __init__(self):
        self.indent_level = 0
        self.output = []
    
    def gen(self, prog: Program) -> str:
        return prog.accept(self)
    
    def indent(self):
        return "    " * self.indent_level
    
    def visit_program(self, node: Program) -> str:
        self.output.append(f"#include <iostream>")
        self.output.append(f"#include <string>")
        self.output.append(f"#include <array>")
        self.output.append(f"#include <cmath>")
        self.output.append(f"")
        self.output.append(f"using namespace std;")
        self.output.append(f"")
        
        for const_decl in node.const_decls:
            const_decl.accept(self)
        
        for type_decl in node.type_decls:
            type_decl.accept(self)
        
        for var_decl in node.decls:
            var_decl.accept(self)
        
        for sub in node.subroutines:
            sub.accept(self)
        
        self.output.append(f"int main() {{")
        self.indent_level += 1
        node.body.accept(self)
        self.indent_level -= 1
        self.output.append(f"    return 0;")
        self.output.append(f"}}")
        
        return "\n".join(self.output)
    
    def visit_const_decl(self, node: ConstDecl):
        cpp_type = self._map_type(node.typ)
        value = self._format_literal(node.value)
        self.output.append(f"const {cpp_type} {node.name} = {value};")
    
    def visit_var_decl(self, node: VarDecl):
        cpp_type = self._map_type(node.typ)
        for name in node.names:
            self.output.append(f"{cpp_type} {name};")
    
    def visit_type_decl(self, node: TypeDecl):
        if isinstance(node.typ, RecordType):
            self.output.append(f"struct {node.name} {{")
            self.indent_level += 1
            node.typ.accept(self)
            self.indent_level -= 1
            self.output.append(f"}};")
            self.output.append(f"")
    
    def visit_record_type(self, node: RecordType):
        for field in node.fields:
            field.accept(self)
    
    def visit_array_type(self, node: ArrayType):
        pass  
    
    def visit_param(self, node: Param):
        pass 
    
    def visit_case_branch(self, node: CaseBranch):
        pass 
    
    def visit_procedure_decl(self, node: ProcedureDecl):
        params = self._format_params(node.params)
        self.output.append(f"void {node.name}({params}) {{")
        self.indent_level += 1
        node.body.accept(self)
        self.indent_level -= 1
        self.output.append(f"}}")
        self.output.append(f"")
    
    def visit_function_decl(self, node: FunctionDecl):
        params = self._format_params(node.params)
        ret_type = self._map_type(node.ret_type)
        self.output.append(f"{ret_type} {node.name}({params}) {{")
        self.indent_level += 1
        node.body.accept(self)
        self.indent_level -= 1
        self.output.append(f"}}")
        self.output.append(f"")
    
    def visit_block(self, node: Block):
        for stmt in node.statements:
            stmt.accept(self)
    
    def visit_assign(self, node: Assign):
        target = self._format_target(node.target)
        expr = node.expr.accept(self)
        self.output.append(f"{self.indent()}{target} = {expr};")
    
    def visit_if(self, node: If):
        cond = node.cond.accept(self)
        self.output.append(f"{self.indent()}if ({cond}) {{")
        self.indent_level += 1
        node.then_branch.accept(self)
        self.indent_level -= 1
        if node.else_branch:
            self.output.append(f"{self.indent()}}} else {{")
            self.indent_level += 1
            node.else_branch.accept(self)
            self.indent_level -= 1
        self.output.append(f"{self.indent()}}}")
    
    def visit_while(self, node: While):
        cond = node.cond.accept(self)
        self.output.append(f"{self.indent()}while ({cond}) {{")
        self.indent_level += 1
        node.body.accept(self)
        self.indent_level -= 1
        self.output.append(f"{self.indent()}}}")
    
    def visit_for(self, node: For):
        start = node.start.accept(self)
        end = node.end.accept(self)
        
        if node.direction == "to":
            self.output.append(f"{self.indent()}for (int {node.var} = {start}; {node.var} <= {end}; {node.var}++) {{")
        else:
            self.output.append(f"{self.indent()}for (int {node.var} = {start}; {node.var} >= {end}; {node.var}--) {{")
        
        self.indent_level += 1
        node.body.accept(self)
        self.indent_level -= 1
        self.output.append(f"{self.indent()}}}")
    
    def visit_repeat(self, node: Repeat):
        self.output.append(f"{self.indent()}do {{")
        self.indent_level += 1
        for stmt in node.body:
            stmt.accept(self)
        self.indent_level -= 1
        cond = node.until_cond.accept(self)
        self.output.append(f"{self.indent()}}} while (!({cond}));")
    
    def visit_case(self, node: Case):
        expr = node.expr.accept(self)
        self.output.append(f"{self.indent()}switch ({expr}) {{")
        
        for branch in node.branches:
            for val in branch.values:
                val_expr = val.accept(self)
                self.output.append(f"{self.indent()}    case {val_expr}:")
                self.indent_level += 1
                branch.stmt.accept(self)
                self.output.append(f"{self.indent()}    break;")
                self.indent_level -= 1
        
        if node.else_branch:
            self.output.append(f"{self.indent()}    default:")
            self.indent_level += 1
            node.else_branch.accept(self)
            self.output.append(f"{self.indent()}    break;")
            self.indent_level -= 1
        
        self.output.append(f"{self.indent()}}}")
    
    def visit_writeln(self, node: Writeln):
        args = [arg.accept(self) for arg in node.args]
        if args:
            self.output.append(f'{self.indent()}cout << {" << ".join(args)} << endl;')
        else:
            self.output.append(f'{self.indent()}cout << endl;')
    
    def visit_readln(self, node: Readln):
        reads = []
        for name in node.args:
            reads.append(f'cin >> {name}')
        self.output.append(f'{self.indent()}{"; ".join(reads)};')
    
    def visit_call(self, node: Call) -> str:
        args = [arg.accept(self) for arg in node.args]
        return f"{node.name}({', '.join(args)})"
    
    def visit_literal(self, node: Literal) -> str:
        if node.lit_type == "string":
            return f'"{node.value}"'
        elif node.lit_type == "char":
            return f"'{node.value}'"
        elif node.lit_type == "boolean":
            return "true" if node.value else "false"
        else:
            return str(node.value)
    
    def visit_identifier(self, node: Identifier) -> str:
        return node.name
    
    def visit_field_access(self, node: FieldAccess) -> str:
        return f"{node.obj}.{node.field}"
    
    def visit_array_access(self, node: ArrayAccess) -> str:
        indexes = [idx.accept(self) for idx in node.indexes]
        if len(indexes) == 1:
            return f"{node.name}[{indexes[0]}]"
        else:
            return f"{node.name}[{']['.join(indexes)}]"
    
    def visit_unary_op(self, node: UnaryOp) -> str:
        operand = node.operand.accept(self)
        if node.op == "not":
            return f"!{operand}"
        else:
            return f"{node.op}{operand}"
    
    def visit_binary_op(self, node: BinaryOp) -> str:
        left = node.left.accept(self)
        right = node.right.accept(self)
        
        op_map = {
            "mod": "%",
            "and": "&&",
            "or": "||",
            "=": "==",
            "<>": "!="
        }
        
        op = op_map.get(node.op, node.op)
        return f"({left} {op} {right})"
    
    def _map_type(self, pascal_type: Union[str, ArrayType, RecordType]) -> str:
        """Преобразование Pascal типа в C++ тип"""
  
        if isinstance(pascal_type, ArrayType):
            return self._map_array_type(pascal_type)
        
        if isinstance(pascal_type, RecordType):
            return "auto"
        
        if isinstance(pascal_type, str):
            type_map = {
                "integer": "int",
                "real": "double",
                "char": "char",
                "boolean": "bool",
                "string": "string"
            }
            return type_map.get(pascal_type, "auto")
        
        return "auto"
    
    def _map_array_type(self, array_type: ArrayType) -> str:
        """Преобразование ArrayType в C++ тип"""
        base_type = self._map_type(array_type.base_type)
        
        dims = []
        for low, high in array_type.ranges:
            dims.append(f"{high - low + 1}")
        
        if len(dims) == 1:
            return f"array<{base_type}, {dims[0]}>"
        else:
            result = f"array<{base_type}, {dims[-1]}>"
            for dim in reversed(dims[:-1]):
                result = f"array<{result}, {dim}>"
            return result
    
    def _format_literal(self, literal: Literal) -> str:
        if literal.lit_type == "string":
            return f'"{literal.value}"'
        elif literal.lit_type == "char":
            return f"'{literal.value}'"
        elif literal.lit_type == "boolean":
            return "true" if literal.value else "false"
        else:
            return str(literal.value)
    
    def _format_params(self, params: List[Param]) -> str:
        param_strs = []
        for param in params:
            cpp_type = self._map_type(param.typ)
            param_strs.append(f"{cpp_type} {param.name}")
        return ", ".join(param_strs)
    
    def _format_target(self, target):
        if isinstance(target, str):
            return target
        elif isinstance(target, FieldAccess):
            return target.accept(self)
        elif isinstance(target, ArrayAccess):
            return target.accept(self)
        return str(target)