from typing import Callable, List, Optional, Self, cast
from abc import ABC, abstractmethod

from lexer import Token, TokenType


class ASTNode(ABC):
    def __init__(self, begin_pos: int, end_pos: int):
        self._begin_pos: int = begin_pos
        self._end_pos: int = end_pos
        self.parent: Optional[ASTNode] = None

    @abstractmethod
    def children(self) -> List['ASTNode']:
        pass

    def replace_child(self, old_child: 'ASTNode', new_child: 'ASTNode'):
        index = self.children().index(old_child)
        if index == -1:
            raise ValueError(f"Child {old_child} not found")
        old_child = self.children()[index]
        for key, value in self.__dict__.items():
            if value is old_child:
                self.__dict__[key] = new_child
                break
        else:
            raise ValueError(f"Child {old_child} not found")
        new_child.parent = self

    def replace_child_at_index(self, index: int, new_child: 'ASTNode'):
        old_child = self.children()[index]
        self.replace_child(old_child, new_child)

    def find_node(self, predicate: Callable[['ASTNode'], bool]) -> Optional['ASTNode']:
        def dfs(node: ASTNode) -> Optional[ASTNode]:
            if predicate(node):
                return node
            for child in node.children():
                result = dfs(child)
                if result:
                    return result
            return None
        
        return dfs(self)
    
    def find_nodes(self, predicate: Callable[['ASTNode'], bool]) -> List['ASTNode']:
        nodes = []
        def dfs(node: 'ASTNode'):
            if predicate(node):
                nodes.append(node)
            for child in node.children():
                dfs(child)
        dfs(self)
        return nodes
    
    def transform(self, transformation: Callable[['ASTNode'], Optional['ASTNode']]) -> None:
        def dfs(node: ASTNode) -> Optional[ASTNode]:
            result = transformation(node)
            if result is not None:
                return result
            
            for i, child in enumerate(node.children()):
                new_child = dfs(child)
                if new_child is not None and new_child is not child:
                    node.replace_child(child, new_child)
            
            return None
        
        dfs(self)

class Statement(ASTNode):
    def __init__(self, begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)

    def children(self) -> List[ASTNode]:
        return []

class Program(ASTNode):
    def __init__(self, statements: List[Statement], comments: List[Token], begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)
        self.statements: List[Statement] = statements
        self.comments: List[Token] = comments
    
    def __str__(self):
        result = self._get_declarations_string()
        if not self.comments:
            return result
        return self._insert_comments(result)

    def _get_declarations_string(self):
        return '\n\n'.join(str(decl) for decl in self.statements)

    def _insert_comments(self, result):
        lines = result.split('\n')
        comment_index = 0
        for i, line in enumerate(lines):
            indent, line_parts = self._get_indent_and_parts(line)
            comment_index = self._process_line_comments(i, line_parts, comment_index)
            lines[i] = indent + ' '.join(line_parts)
        result = '\n'.join(lines)
        return self._add_remaining_comments(result, comment_index)

    def _get_indent_and_parts(self, line):
        line_parts = line.split(' ')
        indent = ''
        if line_parts and not line_parts[0]:
            indent = ' ' * len(line_parts[0])
            line_parts = line_parts[1:]
        return indent, line_parts

    def _process_line_comments(self, line_number, line_parts, comment_index):
        while comment_index < len(self.comments) and self.comments[comment_index].line <= line_number + 1:
            comment = self.comments[comment_index]
            if comment.type == TokenType.LINE_COMMENT:
                line_parts.append(comment.value)
            elif comment.type == TokenType.BLOCK_COMMENT:
                self._insert_block_comment(line_parts, comment)
            comment_index += 1
        return comment_index

    def _insert_block_comment(self, line_parts, comment):
        closest_index = min(range(len(line_parts)), key=lambda j: abs(len(' '.join(line_parts[:j])) - comment.column))
        line_parts.insert(closest_index, comment.value)

    def _add_remaining_comments(self, result, comment_index):
        while comment_index < len(self.comments):
            result += f"\n{self.comments[comment_index].value}"
            comment_index += 1
        return result

    def children(self) -> List[ASTNode]:
        return cast(List[ASTNode], self.statements)

class Type(ASTNode):
    def __init__(self, name: str, specifiers: List[str], pointer_count: Optional[int], begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)
        self.name: str = name
        self.specifiers: List[str] = specifiers
        self.pointer_count: Optional[int] = pointer_count

    def __str__(self):
        result = ""
        if self.specifiers:
            result += ' '.join(self.specifiers) + ' '
        result += self.name
        if self.pointer_count:
            result += '*' * self.pointer_count
        return result

    def children(self) -> List[ASTNode]:
        return []

class CompoundStatement(Statement):
    def __init__(self, statements: List[Statement], begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)
        self.statements: List[Statement] = statements
    
    def __str__(self):
        stmt_strs = []
        for stmt in self.statements:
            if isinstance(stmt, LabelStatement):
                # Do not indent label statements
                stmt_strs.append(str(stmt))
            else:
                stmt_strs.append('    ' + str(stmt).replace('\n', '\n    '))
        NEW_LINE = '\n'
        return f"{{\n{NEW_LINE.join(stmt_strs)}\n}}"

    def children(self) -> List[ASTNode]:
        return cast(List[ASTNode], self.statements)

class Parameter(ASTNode):
    def __init__(self, type: Type, name: str, begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)
        self.type = type
        self.name = name
    
    def __str__(self):
        return f"{self.type} {self.name}"

    def children(self) -> List[ASTNode]:
        return [self.type]

class FunctionDeclaration(Statement):
    def __init__(self, return_type: Type, name: str, parameters: List[Parameter], body: Optional[CompoundStatement], calling_convention: Optional[str], begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)
        self.return_type: Type = return_type
        self.name: str = name
        self.parameters: List[Parameter] = parameters
        self.body: Optional[CompoundStatement] = body
        self.calling_convention: Optional[str] = calling_convention
    
    def __str__(self):
        params = ', '.join(str(param) for param in self.parameters)
        result = str(self.return_type)
        if self.calling_convention:
            result += f" {self.calling_convention}"
        result += f" {self.name}({params})"
        if self.body:
            result += f"\n{self.body}"
        else:
            result += ";"
        return result

    def children(self) -> List[ASTNode]:
        children: List[ASTNode] = [self.return_type]
        children += self.parameters
        if self.body:
            children.append(self.body)
        return children

class Operand(ASTNode):
    def __init__(self, begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)

    def children(self) -> List[ASTNode]:
        return []

class ExpressionStatement(Statement):
    def __init__(self, expression: Operand, begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)
        self.expression: Operand = expression
    
    def __str__(self):
        return f"{self.expression};"

    def children(self) -> List[ASTNode]:
        return [self.expression]

class IfStatement(Statement):
    def __init__(self, condition: Operand, then_branch: Statement, else_branch: Optional[Statement], begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)
        self.condition: Operand = condition
        self.then_branch: Statement = then_branch
        self.else_branch: Optional[Statement] = else_branch
    
    def __str__(self):
        result = f"if ({self.condition})\n{self._indent(self.then_branch)}"
        current_else = self.else_branch
        while isinstance(current_else, IfStatement):
            result += f"\nelse if ({current_else.condition})\n{self._indent(current_else.then_branch)}"
            current_else = current_else.else_branch
        if current_else:
            result += f"\nelse\n{self._indent(current_else)}"
        return result
    
    def _indent(self, operand: Statement):
        if isinstance(operand, CompoundStatement):
            return str(operand)
        return '\n'.join('    ' + line for line in str(operand).split('\n'))

    def children(self) -> List[ASTNode]:
        children = [self.condition, self.then_branch]
        if self.else_branch:
            children.append(self.else_branch)
        return children

class WhileStatement(Statement):
    def __init__(self, condition, body, begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)
        self.condition: Operand = condition
        self.body: Statement = body
    
    def __str__(self):
        return f"while ({self.condition})\n{self.body}"

    def children(self) -> List[ASTNode]:
        return [self.condition, self.body]

class ForStatement(Statement):
    def __init__(self, initializer: Optional[Statement], condition: Optional[Operand], increment: Optional[Operand], body: Statement, begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)
        self.initializer: Optional[Statement] = initializer
        self.condition: Optional[Operand] = condition
        self.increment: Optional[Operand] = increment
        self.body: Statement = body
    
    def __str__(self):
        init_str = str(self.initializer) if self.initializer else ''
        cond_str = str(self.condition) if self.condition else ''
        incr_str = str(self.increment) if self.increment else ''
        return f"for ({init_str} {cond_str}; {incr_str})\n{self._indent(self.body)}"
    
    def _indent(self, operand: Statement):
        if isinstance(operand, CompoundStatement):
            return str(operand)
        return '\n'.join('    ' + line for line in str(operand).split('\n'))

    def children(self) -> List[ASTNode]:
        children = []
        if self.initializer:
            children.append(self.initializer)
        if self.condition:
            children.append(self.condition)
        if self.increment:
            children.append(self.increment)
        children.append(self.body)
        return children

class ReturnStatement(Statement):
    def __init__(self, expression: Optional[Operand], begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)
        self.expression: Optional[Operand] = expression
    
    def __str__(self):
        if self.expression:
            return f"return {self.expression};"
        return "return;"

    def children(self) -> List[ASTNode]:
        return [self.expression] if self.expression else []

class JumpStatement(Statement):
    def __init__(self, jump_type: str, begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)
        self.jump_type: str = jump_type
    
    def __str__(self):
        return f"{self.jump_type};"

    def children(self) -> List[ASTNode]:
        return []

class BinaryOperation(Operand):
    def __init__(self, left: Operand, operator: str, right: Operand, begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)
        self.left: Operand = left
        self.operator: str = operator
        self.right: Operand = right
    
    def __str__(self):
        left_str = str(self.left)
        right_str = str(self.right)
        
        if ((isinstance(self.left, BinaryOperation) and self._needs_parentheses(self.left))
            or isinstance(self.left, CommaOperation)):
            left_str = f"({left_str})"
        
        if ((isinstance(self.right, BinaryOperation) and self._needs_parentheses(self.right))
            or isinstance(self.right, CommaOperation)):
            right_str = f"({right_str})"
        
        return f"{left_str} {self.operator} {right_str}"

    def _needs_parentheses(self, child_op: Self):
        precedence = {
            '*': 3, '/': 3, '%': 3,
            '+': 2, '-': 2,
            '<': 1, '>': 1, '<=': 1, '>=': 1,
            '==': 0, '!=': 0,
            '&&': -1,
            '||': -2
        }
        
        parent_precedence = precedence.get(self.operator, 0)
        child_precedence = precedence.get(child_op.operator, 0)
        
        if parent_precedence > child_precedence:
            return True
        if parent_precedence == child_precedence and self.operator != child_op.operator:
            return True
        return False

    def children(self) -> List[ASTNode]:
        return [self.left, self.right]

class UnaryOperation(Operand):
    def __init__(self, operator: str, operand: Operand, is_postfix: bool, begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)
        self.operator: str = operator
        self.operand: Operand = operand
        self.is_postfix: bool = is_postfix
    
    def __str__(self):
        if self.is_postfix:
            return f"{self.operand}{self.operator}"
        if isinstance(self.operand, BinaryOperation):
            return f"{self.operator}({self.operand})"
        return f"{self.operator}{self.operand}"

    def children(self) -> List[ASTNode]:
        return [self.operand]

class ArrayAccess(Operand):
    def __init__(self, array: Operand, index: Operand, begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)
        self.array: Operand = array
        self.index: Operand = index
    
    def __str__(self):
        return f"{self.array}[{self.index}]"
    
    def children(self) -> List[ASTNode]:
        return [self.array, self.index]

class MemberAccess(Operand):
    def __init__(self, object: Operand, member: Operand, begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)
        self.object: Operand = object
        self.member: Operand = member
    
    def __str__(self):
        return f"{self.object}.{self.member}"
    
    def children(self) -> List[ASTNode]:
        return [self.object, self.member]

class PointerAccess(Operand):
    def __init__(self, pointer: Operand, member: Operand, begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)
        self.pointer: Operand = pointer
        self.member: Operand = member
    
    def __str__(self):
        return f"{self.pointer}->{self.member}"
    
    def children(self) -> List[ASTNode]:
        return [self.pointer, self.member]

class TernaryOperation(Operand):
    def __init__(self, condition: Operand, true_branch: Operand, false_branch: Operand, begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)
        self.condition: Operand = condition
        self.true_branch: Operand = true_branch
        self.false_branch: Operand = false_branch
    
    def __str__(self):
        return f"({self.condition} ? {self.true_branch} : {self.false_branch})"
    
    def children(self) -> List[ASTNode]:
        return [self.condition, self.true_branch, self.false_branch]

class Literal(Operand):
    def __init__(self, value: str, begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)
        self.value: str = value
    
    def __str__(self):
        return self.value
    
    def children(self) -> List[ASTNode]:
        return []

class StringLiteral(Literal):
    pass # value should already have quotes
    
    def children(self) -> List[ASTNode]:
        return []

class Identifier(Operand):
    def __init__(self, name: str, begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)
        self.name: str = name
    
    def __str__(self):
        return self.name
    
    def children(self) -> List[ASTNode]:
        return []

class FunctionCall(Operand):
    def __init__(self, function: Operand, arguments: List[Operand], begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)
        self.function = function
        self.arguments = arguments
    
    def __str__(self):
        if not self.arguments:
            return f"{self.function}()"
        args = ', '.join(str(arg) for arg in self.arguments)
        if isinstance(self.function, UnaryOperation):
            return f"({self.function})({args})"
        return f"{self.function}({args})"
    
    def children(self) -> List[ASTNode]:
        children: List[ASTNode] = [self.function]
        return children + self.arguments

class VariableDeclaration(Statement):
    def __init__(self, type: Type, name: str, initializer: Optional[Operand], begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)
        self.type: Type = type
        self.name: str = name
        self.initializer: Optional[Operand] = initializer
    
    def __str__(self):
        if self.initializer:
            return f"{self.type} {self.name} = {self.initializer};"
        return f"{self.type} {self.name};"
    
    def children(self) -> List[ASTNode]:
        children: List[ASTNode] = [self.type]
        if self.initializer:
            children.append(self.initializer)
        return children

class GotoStatement(Statement):
    def __init__(self, label: str, begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)
        self.label: str = label
    
    def __str__(self):
        return f"goto {self.label};"
    
    def children(self) -> List[ASTNode]:
        return []

class LabelStatement(Statement):
    def __init__(self, label: str, begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)
        self.label: str = label
    
    def __str__(self):
        return f"{self.label}:"
    
    def children(self) -> List[ASTNode]:
        return []

class CommaOperation(BinaryOperation):
    def __init__(self, left: Operand, right: Operand, begin_pos: int, end_pos: int):
        super().__init__(left, ',', right, begin_pos, end_pos)
    
    def __str__(self):
        return f"{self.left}, {self.right}"
    
    def children(self) -> List[ASTNode]:
        return cast(List[ASTNode], [self.left, self.right])

class SwitchStatement(Statement):
    def __init__(self, expression: Operand, body: CompoundStatement, begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)
        self.expression: Operand = expression
        self.body: CompoundStatement = body
    
    def __str__(self):
        return f"switch ({self.expression})\n{self.body}"

    def children(self) -> List[ASTNode]:
        return [self.expression, self.body]

class CaseStatement(Statement):
    def __init__(self, value: Optional[Operand], statement: Statement, begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)
        self.value: Optional[Operand] = value
        self.statement: Statement = statement
    
    def __str__(self):
        if self.is_default_statement():
            return f"default:\n    {self.statement}"
        return f"case {self.value}:\n    {self.statement}"

    def children(self) -> List[ASTNode]:
        children = cast(List[ASTNode], [self.statement])
        if self.value:
            children.insert(0, self.value)
        return children
    
    def is_default_statement(self):
        return self.value is None