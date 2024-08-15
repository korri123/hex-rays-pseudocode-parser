from typing import Optional
from ast_nodes import ASTNode, FunctionCall, Identifier, MemberAccess, PointerAccess


# object->vtbl->function -> object->function
def transform_function_call(node: ASTNode) -> Optional[ASTNode]:
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