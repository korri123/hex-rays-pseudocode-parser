
from typing import Callable, Optional, List, Self, Tuple, cast
from enum import Enum, auto
from abc import ABC, abstractmethod

C_VOID_TYPE = {'void'}
C_INT_TYPES = {'int', 'char', 'short', 'long', 'long long'}
C_FLOAT_TYPES = {'float', 'double'}
MSVC_CALLING_CONVENTIONS = {'__stdcall', '__cdecl', '__fastcall', '__thiscall', '__vectorcall'}

C_DECLARATION_SPECIFIERS = {'static', 'extern', 'auto', 'register', 'const', 'volatile', 'inline', 'unsigned', 'thread_local'}

C_KEYWORDS = { 'if', 'else', 'while', 'for', 'return', 'static', 'const', 
                      'break', 'continue', 'goto', 'case', 'default', 'switch', 'enum', 'typedef', 'struct', 'union', 'volatile', 
                      'register', 'auto', 'extern', 'sizeof', 'volatile', 'inline', 'restrict', 'alignas', 'alignof', 
                      'static_assert'}

C_KEYWORDS |= C_DECLARATION_SPECIFIERS

C_OPERATORS = {'+', '-', '*', '/', '=', '<', '>', '!', '&', '|', '^', '~', ';', '->', '++', '--', '+=', '-=', '*=', 
               '/=', '%=', '&=', '|=', '^=', '<<=', '>>=', '==', '!=', '<=', '>=', '&&', '||', '<<', '>>', '%', '?', 
               ':', '.', ',', '(', ')', '[', ']', '{', '}'}
# Add the '::' operator to the list of C operators since it can be in the function name in pseudocode
C_OPERATORS |= {'::'}
IDA_PSEUDOCODE_OPERATORS = {'LOBYTE', 'HIBYTE', 'WORD', 'DWORD', 'QWORD', 'BYTE'}

class TokenType(Enum):
    KEYWORD = auto()
    IDENTIFIER = auto()
    NUMBER = auto()
    OPERATOR = auto()
    STRING = auto()
    LINE_COMMENT = auto()
    BLOCK_COMMENT = auto()
    EOF = auto()

class Token:
    def __init__(self, type: TokenType, value: str, line: int, column: int, position: int):
        self.type: TokenType = type
        self.value: str = value
        self.line: int = line
        self.column: int = column
        self.position: int = position
    
    def __str__(self):
        return self.value

class Lexer:
    def __init__(self, code: str = ""):
        self.code: str = code
        self.position: int = 0
        self.line: int = 1
        self.column: int = 1

    def set_code(self, code: str):
        self.code = code
        self.position = 0
        self.line = 1
        self.column = 1

    def next_token(self) -> Token:
        if self.position >= len(self.code):
            return Token(TokenType.EOF, '', self.line, self.column, self.position)

        char: str = self.code[self.position]

        # Skip whitespace
        if char.isspace():
            self.advance()
            return self.next_token()

        # Comments
        if char == '/' and self.peek() == '/':
            return self.line_comment()
        if char == '/' and self.peek() == '*':
            return self.block_comment()

        # Identifiers and keywords
        if char.isalpha() or char == '_':
            return self.identifier()

        # Numbers
        if char.isdigit():
            return self.number()

        # Operators and punctuation
        if char in C_OPERATORS:
            return self.operator()

        # String literals
        if char in '"\'':
            return self.string()

        # Unrecognized character
        raise self.error(f"Unexpected character: {char}")

    def identifier(self) -> Token:
        start: int = self.position
        while self.position < len(self.code) and (self.code[self.position].isalnum() or self.code[self.position] == '_'):
            self.advance()
        value: str = self.code[start:self.position]
        
        if value in C_KEYWORDS:
            return Token(TokenType.KEYWORD, value, self.line, self.column - (self.position - start), self.position)
        peek = self.peek_next_token()
        while peek.type == TokenType.OPERATOR and peek.value == '::':
            self.operator()
            peek = self.peek_next_token()
            if peek.type not in [TokenType.IDENTIFIER, TokenType.NUMBER]:
                break
            identifier = self.identifier()
            value = f"{value}::{identifier.value}"
            peek = self.peek_next_token()
        return Token(TokenType.IDENTIFIER, value, self.line, self.column - (self.position - start), self.position)

    def number(self) -> Token:
        start: int = self.position
        if self.code[self.position:self.position+2].lower() == '0x':
            # Hexadecimal number
            self.advance(2)
            while self.position < len(self.code) and (self.code[self.position].isdigit() or self.code[self.position].lower() in 'abcdef'):
                self.advance()
        elif self.code[self.position:self.position+2].lower() == '0b':
            # Binary number
            self.advance(2)
            while self.position < len(self.code) and self.code[self.position] in '01':
                self.advance()
        else:
            # Decimal number
            while self.position < len(self.code) and self.code[self.position].isdigit():
                self.advance()
            if self.position < len(self.code) and self.code[self.position] == '.':
                self.advance()
                while self.position < len(self.code) and self.code[self.position].isdigit():
                    self.advance()
        value: str = self.code[start:self.position]
        return Token(TokenType.NUMBER, value, self.line, self.column - (self.position - start), self.position)

    def operator(self) -> Token:
        current_op: str = self.code[self.position]
        self.advance()

        if self.position >= len(self.code):
            return Token(TokenType.OPERATOR, current_op, self.line, self.column - len(current_op), self.position)

        next_char: str = self.code[self.position]
        potential_op: str = current_op + next_char
        
        if potential_op not in C_OPERATORS:
            return Token(TokenType.OPERATOR, current_op, self.line, self.column - len(current_op), self.position)

        self.advance()
        current_op = potential_op

        if self.position >= len(self.code):
            return Token(TokenType.OPERATOR, current_op, self.line, self.column - len(current_op), self.position)

        next_char = self.code[self.position]
        potential_op = current_op + next_char
        if potential_op in C_OPERATORS:
            self.advance()
            current_op = potential_op

        return Token(TokenType.OPERATOR, current_op, self.line, self.column - len(current_op), self.position)

    def string(self) -> Token:
        start: int = self.position
        quote: str = self.code[self.position]
        self.advance()
        while self.position < len(self.code) and self.code[self.position] != quote:
            if self.code[self.position] == '\\':
                self.advance()
            self.advance()
        if self.position >= len(self.code):
            self.error("Unterminated string literal")
        self.advance()  # Consume closing quote
        value: str = self.code[start:self.position]
        return Token(TokenType.STRING, value, self.line, self.column - (self.position - start), self.position)

    def line_comment(self) -> Token:
        start: int = self.position
        while self.position < len(self.code) and self.code[self.position] != '\n':
            self.advance()
        value: str = self.code[start:self.position]
        return Token(TokenType.LINE_COMMENT, value, self.line, self.column - (self.position - start), self.position)

    def block_comment(self) -> Token:
        start: int = self.position
        self.advance(2)  # Skip /*
        while self.position < len(self.code) - 1 and (self.code[self.position] != '*' or self.code[self.position + 1] != '/'):
            self.advance()
        if self.position >= len(self.code) - 1:
            self.error("Unterminated block comment")
        self.advance(2)  # Skip */
        value: str = self.code[start:self.position]
        return Token(TokenType.BLOCK_COMMENT, value, self.line, self.column - (self.position - start), self.position)

    def advance(self, count: int = 1) -> None:
        for _ in range(count):
            if self.position < len(self.code):
                if self.code[self.position] == '\n':
                    self.line += 1
                    self.column = 1
                else:
                    self.column += 1
                self.position += 1

    def peek(self) -> Optional[str]:
        if self.position + 1 < len(self.code):
            return self.code[self.position + 1]
        return None

    def peek_next_token(self) -> Token:
        current_position = self.position
        current_line = self.line
        current_column = self.column
        next_token = self.next_token()
        self.position = current_position
        self.line = current_line
        self.column = current_column
        return next_token

    def error(self, message: str) -> Exception:
        return Exception(f"Lexer error at line {self.line}, column {self.column}: {message}")

class ASTNode(ABC):
    def __init__(self, begin_pos: int, end_pos: int):
        self.begin_pos: int = begin_pos
        self.end_pos: int = end_pos
        self.parent: Optional[ASTNode] = None

    @abstractmethod
    def children(self) -> List['ASTNode']:
        pass

    def replace_child(self, old_child: Self, new_child: Self):
        index = self.children().index(old_child)
        if index == -1:
            raise ValueError(f"Child {old_child} not found")
        old_child = self.children()[index]
        for key, value in self.__dict__.items():
            if value == old_child:
                self.__dict__[key] = new_child
                break
        else:
            raise ValueError(f"Child {old_child} not found")
        new_child.parent = self

    def replace_child_at_index(self, index: int, new_child: Self):
        old_child = self.children()[index]
        self.replace_child(old_child, new_child)

    def find_node(self, predicate: Callable[[Self], bool]) -> Optional[Self]:
        def dfs(node: ASTNode) -> Optional[ASTNode]:
            if predicate(node):
                return node
            for child in node.children():
                result = dfs(child)
                if result:
                    return result
            return None
        
        return dfs(self)
    
    def transform(self, transformation: Callable[[Self], Optional[Self]]) -> None:
        def dfs(node: ASTNode) -> Optional[ASTNode]:
            result = transformation(node)
            if result is not None:
                return result
            
            for i, child in enumerate(node.children()):
                new_child = dfs(child)
                if new_child is not None and new_child is not child:
                    node.replace_child_at_index(i, new_child)
            
            return None
        
        dfs(self)

class Program(ASTNode):
    def __init__(self, statements, comments, begin_pos: int, end_pos: int):
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

class Statement(ASTNode):
    def __init__(self, begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)

    def children(self) -> List[ASTNode]:
        return []

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

class IDAOperator(Operand):
    def __init__(self, operator: str, operand: Operand, begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)
        self.operator: str = operator
        self.operand: Operand = operand
    
    def __str__(self):
        return f"{self.operator}({self.operand})"
    
    def children(self) -> List[ASTNode]:
        return [self.operand]

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
        if self.value is None:
            return f"default:\n    {self.statement}"
        return f"case {self.value}:\n    {self.statement}"

    def children(self) -> List[ASTNode]:
        children = cast(List[ASTNode], [self.statement])
        if self.value:
            children.insert(0, self.value)
        return children

class ParserException(Exception):
    pass

class Parser:
    def __init__(self, lexer: Optional[Lexer] = None, code: str = ""):
        if lexer is None:
            self.lexer = Lexer()
        else:
            self.lexer = lexer
        
        if code:
            self.lexer.set_code(code)
        
        self.current_token: Token = self.lexer.next_token()
        self._comments: List[Token] = []
        self._rest: str = self.lexer.code[self.lexer.position:]
        self._position_stack = []

    @property
    def position(self):
        return self.lexer.position
    
    @position.setter
    def position(self, value):
        self.lexer.position = value

    @property
    def _dbg_token(self):
        return (self.current_token.value, self.current_token.type)
    
    def parse(self) -> Program:
        declarations = []
        while self.current_token.type != TokenType.EOF:
            declarations.append(self.parse_statement())
        program = Program(declarations, self._comments, 0, self.position)
        self.assign_parents(program)
        return program

    def assign_parents(self, node: ASTNode):
        for child in node.children():
            child.parent = node
            self.assign_parents(child)

    def parse_declaration_specifiers(self) -> List[str]:
        specifiers = []
        while self.is_declaration_specifier(self.current_token):
            specifiers.append(self.current_token.value)
            self.advance()
        return specifiers

    def is_declaration_specifier(self, token: Token) -> bool:
        return (token.type == TokenType.KEYWORD and token.value in C_DECLARATION_SPECIFIERS)

    def parse_type(self) -> Type:
        declaration_specifiers = self.parse_declaration_specifiers()
        _type = self.expect(TokenType.IDENTIFIER)
        pointer_count = 0
        while self.current_token.type == TokenType.OPERATOR and self.current_token.value == '*':
            pointer_count += 1
            self.advance()
        return Type(_type.value, declaration_specifiers, pointer_count, _type.position, self.position)

    def parse_parameters(self) -> List[Parameter]:
        parameters = []
        while self.current_token.type != TokenType.OPERATOR or self.current_token.value != ')':
            param_type = self.parse_type()
            param_name = self.expect(TokenType.IDENTIFIER)
            parameters.append(Parameter(param_type, param_name.value, param_type.begin_pos, param_name.position))
            if self.current_token.type == TokenType.OPERATOR and self.current_token.value == ',':
                self.advance()
        return parameters

    def parse_compound_statement(self) -> CompoundStatement:
        start_pos = self.current_token.position
        self.expect(TokenType.OPERATOR, '{')
        statements = []
        while self.current_token.type != TokenType.OPERATOR or self.current_token.value != '}':
            statements.append(self.parse_statement())
        self.expect(TokenType.OPERATOR, '}')
        return CompoundStatement(statements, start_pos, self.current_token.position)
    
    def push_position(self):
        state = (self.lexer.position, self.current_token, self._comments.copy())
        self._position_stack.append(state)

    def pop_position(self):
        if not self._position_stack:
            raise ParserException("Attempted to pop from an empty position stack")
        position, token, comments = self._position_stack.pop()
        self.lexer.position = position
        self.current_token = token
        self._comments = comments
        self._rest = self.lexer.code[self.lexer.position:]

    def with_preserved_position(self, func):
        self.push_position()
        try:
            return func()
        finally:
            self.pop_position()

    def is_variable_declaration(self) -> bool:
        def check():
            try:
                self.parse_type()
                self.expect(TokenType.IDENTIFIER)  # name
                operator = self.expect(TokenType.OPERATOR)
                return operator.value in ('=', ';')
            except ParserException:
                return False

        return self.with_preserved_position(check)

    def is_function_declaration(self) -> bool:
        def check():
            try:
                self.parse_function_signature()
                self.expect(TokenType.OPERATOR, '(')
                return True
            except ParserException:
                return False

        return self.with_preserved_position(check)

    def parse_statement(self) -> Statement:        
        if self.current_token.value == 'if':
            return self.parse_if_statement()
        elif self.current_token.value == 'while':
            return self.parse_while_statement()
        elif self.current_token.value == 'for':
            return self.parse_for_statement()
        elif self.current_token.value == 'return':
            return self.parse_return_statement()
        elif self.current_token.value == 'switch':
            return self.parse_switch_statement()
        elif self.current_token.value == 'case':
            return self.parse_case_statement()
        elif self.current_token.value == 'default':
            return self.parse_default_statement()
        elif self.current_token.type == TokenType.OPERATOR and self.current_token.value == '{':
            return self.parse_compound_statement()
        elif self.is_variable_declaration():
            return self.parse_variable_declaration()
        elif self.is_function_declaration():
            return self.parse_function_declaration()
        elif self.current_token.value == 'goto':
            return self.parse_goto_statement()
        elif self.is_label():
            return self.parse_label_statement()
        else:
            return self.parse_expression_statement()

    def parse_goto_statement(self) -> GotoStatement:
        start_pos = self.current_token.position
        self.expect(TokenType.KEYWORD, 'goto')
        label = self.expect(TokenType.IDENTIFIER)
        self.expect(TokenType.OPERATOR, ';')
        return GotoStatement(label.value, start_pos, self.current_token.position)

    def is_label(self) -> bool:
        if self.current_token.type != TokenType.IDENTIFIER:
            return False
        next_token = self.lexer.peek_next_token()
        return next_token.type == TokenType.OPERATOR and next_token.value == ':'

    def parse_label_statement(self) -> LabelStatement:
        start_pos = self.current_token.position
        label = self.expect(TokenType.IDENTIFIER)
        self.expect(TokenType.OPERATOR, ':')
        return LabelStatement(label.value, start_pos, self.current_token.position)

    def parse_variable_declaration(self) -> VariableDeclaration:
        start_pos = self.current_token.position
        var_type = self.parse_type()
        var_name = self.expect(TokenType.IDENTIFIER)
        initializer = None
        if self.current_token.type == TokenType.OPERATOR and self.current_token.value == '=':
            self.advance()
            initializer = self.parse_expression()
        self.expect(TokenType.OPERATOR, ';')
        return VariableDeclaration(var_type, var_name.value, initializer, start_pos, self.current_token.position)

    def parse_function_signature(self) -> Tuple[Type, Token, Optional[str]]:
        _type = self.parse_type()
        _name = self.expect(TokenType.IDENTIFIER)
        calling_convention = None
        if _name.value in MSVC_CALLING_CONVENTIONS:
            calling_convention = _name.value
            _name = self.expect(TokenType.IDENTIFIER)
        return _type, _name, calling_convention

    def parse_function_declaration(self) -> FunctionDeclaration:
        start_pos = self.current_token.position
        _type, _name, calling_convention = self.parse_function_signature()
        self.expect(TokenType.OPERATOR, '(')
        parameters = self.parse_parameters()
        self.expect(TokenType.OPERATOR, ')')
        if self.current_token.type == TokenType.OPERATOR and self.current_token.value == ';':
            body = None
            self.advance()
        else:
            body = self.parse_compound_statement()
        return FunctionDeclaration(_type, _name.value, parameters, body, calling_convention, start_pos, self.current_token.position)

    def parse_if_statement(self) -> IfStatement:
        start_pos = self.current_token.position
        self.expect(TokenType.KEYWORD, 'if')
        self.expect(TokenType.OPERATOR, '(')
        condition = self.parse_comma_expression()
        self.expect(TokenType.OPERATOR, ')')
        then_branch = self.parse_statement()
        else_branch = None
        if self.current_token.type == TokenType.KEYWORD and self.current_token.value == 'else':
            self.advance()
            else_branch = self.parse_statement()
        return IfStatement(condition, then_branch, else_branch, start_pos, self.current_token.position)

    def parse_while_statement(self) -> WhileStatement:
        start_pos = self.current_token.position
        self.expect(TokenType.KEYWORD, 'while')
        self.expect(TokenType.OPERATOR, '(')
        condition = self.parse_expression()
        self.expect(TokenType.OPERATOR, ')')
        body = self.parse_statement()
        return WhileStatement(condition, body, start_pos, self.current_token.position)

    def parse_for_statement(self) -> ForStatement:
        start_pos = self.current_token.position
        self.expect(TokenType.KEYWORD, 'for')
        self.expect(TokenType.OPERATOR, '(')
        
        # Parse initializer
        initializer = None
        if self.current_token.type != TokenType.OPERATOR or self.current_token.value != ';':
            if self.is_variable_declaration():
                initializer = self.parse_variable_declaration()
            else:
                initializer = self.parse_expression_statement()
        else:
            self.advance()  # Skip the semicolon

        # Parse condition
        condition = None
        if self.current_token.type != TokenType.OPERATOR or self.current_token.value != ';':
            condition = self.parse_expression()
        self.expect(TokenType.OPERATOR, ';')

        # Parse increment
        increment = None
        if self.current_token.type != TokenType.OPERATOR or self.current_token.value != ')':
            increment = self.parse_expression()
        self.expect(TokenType.OPERATOR, ')')

        # Parse body
        body = self.parse_statement()

        return ForStatement(initializer, condition, increment, body, start_pos, self.current_token.position)

    def parse_return_statement(self) -> ReturnStatement:
        start_pos = self.current_token.position
        self.expect(TokenType.KEYWORD, 'return')
        expression = None
        if self.current_token.type != TokenType.OPERATOR or self.current_token.value != ';':
            expression = self.parse_expression()
        self.expect(TokenType.OPERATOR, ';')
        return ReturnStatement(expression, start_pos, self.current_token.position)

    def parse_expression_statement(self) -> ExpressionStatement:
        start_pos = self.current_token.position
        expression = self.parse_expression()
        self.expect(TokenType.OPERATOR, ';')
        return ExpressionStatement(expression, start_pos, self.current_token.position)

    def parse_expression(self) -> Operand:
        return self.parse_comma_expression()

    def parse_comma_expression(self) -> Operand:
        start_pos = self.current_token.position
        expr = self.parse_assignment()
        if self.current_token.type == TokenType.OPERATOR and self.current_token.value == ',':
            self.advance()
            right = self.parse_expression()
            return CommaOperation(expr, right, start_pos, self.current_token.position)
        return expr
    
    def parse_argument(self) -> Operand:
        # we skip parsing of comma expressions here
        return self.parse_assignment()

    def parse_assignment(self) -> Operand:
        start_pos = self.current_token.position
        left = self.parse_logical_or()
        if self.current_token.type == TokenType.OPERATOR and self.current_token.value in ['=', '+=', '-=', '*=', '/=', '%=', '&=', '|=', '^=', '<<=', '>>=']:
            op = self.current_token
            self.advance()
            right = self.parse_assignment()
            return BinaryOperation(left, op.value, right, start_pos, self.current_token.position)
        return left

    def parse_logical_or(self) -> Operand:
        start_pos = self.current_token.position
        expr = self.parse_logical_and()
        while self.current_token.type == TokenType.OPERATOR and self.current_token.value == '||':
            op = self.current_token
            self.advance()
            right = self.parse_logical_and()
            expr = BinaryOperation(expr, op.value, right, start_pos, self.current_token.position)
        return expr

    def parse_logical_and(self) -> Operand:
        start_pos = self.current_token.position
        expr = self.parse_equality()
        while self.current_token.type == TokenType.OPERATOR and self.current_token.value == '&&':
            op = self.current_token
            self.advance()
            right = self.parse_bitwise_or()
            expr = BinaryOperation(expr, op.value, right, start_pos, self.current_token.position)
        return expr
    
    def parse_bitwise_or(self) -> Operand:
        start_pos = self.current_token.position
        expr = self.parse_bitwise_xor()
        while self.current_token.type == TokenType.OPERATOR and self.current_token.value == '|':
            op = self.current_token
            self.advance()
            right = self.parse_bitwise_xor()
            expr = BinaryOperation(expr, op.value, right, start_pos, self.current_token.position)
        return expr

    def parse_bitwise_xor(self) -> Operand:
        start_pos = self.current_token.position
        expr = self.parse_bitwise_and()
        while self.current_token.type == TokenType.OPERATOR and self.current_token.value == '^':
            op = self.current_token
            self.advance()
            right = self.parse_bitwise_and()
            expr = BinaryOperation(expr, op.value, right, start_pos, self.current_token.position)
        return expr

    def parse_bitwise_and(self) -> Operand:
        start_pos = self.current_token.position
        expr = self.parse_equality()
        while self.current_token.type == TokenType.OPERATOR and self.current_token.value == '&':
            op = self.current_token
            self.advance()
            right = self.parse_equality()
            expr = BinaryOperation(expr, op.value, right, start_pos, self.current_token.position)
        return expr

    def parse_equality(self) -> Operand:
        start_pos = self.current_token.position
        expr = self.parse_relational()
        while self.current_token.type == TokenType.OPERATOR and self.current_token.value in ['==', '!=']:
            op = self.current_token
            self.advance()
            right = self.parse_relational()
            expr = BinaryOperation(expr, op.value, right, start_pos, self.current_token.position)
        return expr

    def parse_relational(self) -> Operand:
        start_pos = self.current_token.position
        expr = self.parse_additive()
        while self.current_token.type == TokenType.OPERATOR and self.current_token.value in ['<', '>', '<=', '>=']:
            op = self.current_token
            self.advance()
            right = self.parse_additive()
            expr = BinaryOperation(expr, op.value, right, start_pos, self.current_token.position)
        return expr

    def parse_additive(self) -> Operand:
        start_pos = self.current_token.position
        expr = self.parse_multiplicative()
        while self.current_token.type == TokenType.OPERATOR and self.current_token.value in ['+', '-']:
            op = self.current_token
            self.advance()
            right = self.parse_multiplicative()
            expr = BinaryOperation(expr, op.value, right, start_pos, self.current_token.position)
        return expr

    def parse_multiplicative(self) -> Operand:
        start_pos = self.current_token.position
        expr = self.parse_unary()
        while self.current_token.type == TokenType.OPERATOR and self.current_token.value in ['*', '/', '%']:
            op = self.current_token
            self.advance()
            right = self.parse_unary()
            expr = BinaryOperation(expr, op.value, right, start_pos, self.current_token.position)
        return expr

    def parse_unary(self) -> Operand:
        start_pos = self.current_token.position
        if self.current_token.type == TokenType.OPERATOR and self.current_token.value in ['-', '!', '*', '&', '~', '++', '--']:
            op = self.current_token
            self.advance()
            expr = self.parse_unary()
            return UnaryOperation(op.value, expr, False, start_pos, self.current_token.position)
        return self.parse_postfix()

    def parse_postfix(self) -> Operand:
        expr = self.parse_primary()
        start_pos = expr.begin_pos

        while self.current_token.type == TokenType.OPERATOR:
            if self.current_token.value in ['++', '--']:
                op = self.current_token
                self.advance()
                expr = UnaryOperation(op.value, expr, True, start_pos, self.current_token.position)
            elif self.current_token.value == '(':
                expr = self.parse_function_call(expr, start_pos)
            elif self.current_token.value == '[':
                self.advance()
                index = self.parse_expression()
                self.expect(TokenType.OPERATOR, ']')
                expr = ArrayAccess(expr, index, start_pos, self.current_token.position)
            elif self.current_token.value == '.':
                self.advance()
                member = self.parse_primary()
                expr = MemberAccess(expr, member, start_pos, self.current_token.position)
            elif self.current_token.value == '->':
                self.advance()
                member = self.parse_primary()
                expr = PointerAccess(expr, member, start_pos, self.current_token.position)
            else:
                break

        return expr

    def parse_primary(self) -> Operand:
        start_pos = self.current_token.position
        expr = None

        if (self.current_token.type == TokenType.IDENTIFIER and 
            self.current_token.value in IDA_PSEUDOCODE_OPERATORS):
            operator = self.current_token.value
            self.advance()
            self.expect(TokenType.OPERATOR, '(')
            operand = self.parse_expression()
            self.expect(TokenType.OPERATOR, ')')
            expr = IDAOperator(operator, operand, start_pos, self.current_token.position)
        elif self.current_token.type == TokenType.NUMBER:
            value = self.current_token.value
            self.advance()
            expr = Literal(value, start_pos, self.current_token.position)
        elif self.current_token.type == TokenType.IDENTIFIER:
            name = self.current_token.value
            self.advance()
            expr = Identifier(name, start_pos, self.current_token.position)
        elif self.current_token.type == TokenType.OPERATOR and self.current_token.value == '(':
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.OPERATOR, ')')
        elif self.current_token.type == TokenType.STRING:
            value = self.current_token.value
            self.advance()
            expr = StringLiteral(value, start_pos, self.current_token.position)
        else:
            raise self.error(f"Unexpected token: {self.current_token}")

        return expr

    def parse_function_call(self, function: Operand, start_pos: int) -> FunctionCall:
        self.expect(TokenType.OPERATOR, '(')
        arguments = []
        if self.current_token.type != TokenType.OPERATOR or self.current_token.value != ')':
            arguments.append(self.parse_expression())
            while self.current_token.type == TokenType.OPERATOR and self.current_token.value == ',':
                self.advance()
                arguments.append(self.parse_argument())
        self.expect(TokenType.OPERATOR, ')')
        return FunctionCall(function, arguments, start_pos, self.current_token.position)

    def parse_switch_statement(self) -> SwitchStatement:
        start_pos = self.current_token.position
        self.expect(TokenType.KEYWORD, 'switch')
        self.expect(TokenType.OPERATOR, '(')
        expression = self.parse_expression()
        self.expect(TokenType.OPERATOR, ')')
        body = self.parse_compound_statement()
        return SwitchStatement(expression, body, start_pos, self.current_token.position)

    def parse_case_statement(self) -> CaseStatement:
        start_pos = self.current_token.position
        self.expect(TokenType.KEYWORD, 'case')
        value = self.parse_expression()
        self.expect(TokenType.OPERATOR, ':')
        statement = self.parse_statement()
        return CaseStatement(value, statement, start_pos, self.current_token.position)

    def parse_default_statement(self) -> CaseStatement:
        start_pos = self.current_token.position
        self.expect(TokenType.KEYWORD, 'default')
        self.expect(TokenType.OPERATOR, ':')
        statement = self.parse_statement()
        return CaseStatement(None, statement, start_pos, self.current_token.position)

    def advance(self):
        self.current_token = self.lexer.next_token()
        while self.current_token.type in (TokenType.LINE_COMMENT, TokenType.BLOCK_COMMENT):
            self._comments.append(self.current_token)
            self.current_token = self.lexer.next_token()
        self.position = self.current_token.position
        self._rest = self.lexer.code[self.position:]

    def expect(self, token_type: TokenType, value: Optional[str] = None) -> Token:
        if self.current_token.type != token_type:
            raise self.error(f"Expected token type {token_type}, but got {self.current_token.type}")
        if value is not None and self.current_token.value != value:
            raise self.error(f"Expected token value '{value}', but got '{self.current_token.value}'")
        token = self.current_token
        self.advance()
        return token

    def error(self, message: str):
        return ParserException(f"Parser error: {message}")
