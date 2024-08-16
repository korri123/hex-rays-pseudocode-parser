from typing import Optional
from ast_nodes import ASTNode, FunctionCall, FunctionDeclaration, Identifier, MemberAccess, PointerAccess, CommaOperation, BinaryOperation


# void __thiscall function(void* this) -> void function()
# void __cdecl function() -> void function()
def remove_calling_convention(node: ASTNode) -> Optional[ASTNode]:
    if isinstance(node, FunctionDeclaration):
        calling_convention = node.calling_convention
        if calling_convention == '__thiscall' and node.parameters:
            node.parameters = node.parameters[1:]
        node.calling_convention = None
        return node
    return None

# object->vtbl->function(object) -> object->function()
def remove_vtbl_and_first_arg(node: ASTNode) -> Optional[ASTNode]:
    if isinstance(node, FunctionCall):
        if isinstance(node.function, PointerAccess) and isinstance(node.function.pointer, PointerAccess):
            vtbl_access = node.function.pointer
            if isinstance(vtbl_access.member, Identifier) and vtbl_access.member.name == 'vtbl':
                # Preserve the object identifier
                object_identifier = vtbl_access.pointer
                # Remove vtbl, but keep the object identifier
                new_function = PointerAccess(object_identifier, node.function.member, node.function._begin_pos, node.function._end_pos)
                # Remove first argument (object)
                new_arguments = node.arguments[1:] if node.arguments else []
                return FunctionCall(new_function, new_arguments, node._begin_pos, node._end_pos)
    return None

# this->data.baseProcess -> this->baseProcess
def remove_data_arrow(node: ASTNode) -> Optional[ASTNode]:
    if isinstance(node, MemberAccess):
        if isinstance(node.object, PointerAccess) and isinstance(node.object.member, Identifier) and node.object.member.name == 'data':
            return PointerAccess(node.object.pointer, node.member, node._begin_pos, node._end_pos)
    return None

# (v1 = 1, v1 == 1) -> 1 == 1
def inline_comma_assignment(node: ASTNode) -> Optional[ASTNode]:
    if isinstance(node, CommaOperation):
        left = node.left
        right = node.right
        if isinstance(left, BinaryOperation) and left.operator == '=':
            assigned_var = left.left
            assigned_value = left.right
            if isinstance(assigned_var, Identifier):
                # Replace all occurrences of the assigned variable in the right operand
                def replace_var(n: ASTNode) -> Optional[ASTNode]:
                    if isinstance(n, Identifier) and n.name == assigned_var.name:
                        return assigned_value
                    return None
                
                new_right = right.transform(replace_var)
                return new_right
    return None

def apply_refactorings(ast: ASTNode) -> ASTNode:
    # Apply the transformations to the AST
    while True:
        ast_before = str(ast)
        ast.transform(remove_vtbl_and_first_arg)
        ast.transform(remove_data_arrow)
        ast.transform(inline_comma_assignment)
        ast.transform(remove_calling_convention)
        ast_after = str(ast)
        
        if ast_before == ast_after:
            break
    return ast