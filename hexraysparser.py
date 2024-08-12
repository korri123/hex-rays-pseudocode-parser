
import re
from typing import Optional, List
from enum import Enum, auto

C_VOID_TYPE = {'void'}
C_INT_TYPES = {'int', 'char', 'short', 'long', 'long long'}
C_FLOAT_TYPES = {'float', 'double'}

def is_c_basic_type(type: str) -> bool:
    return type in C_VOID_TYPE or type in C_INT_TYPES or type in C_FLOAT_TYPES

C_DECLARATION_SPECIFIERS = {'static', 'extern', 'auto', 'register', 'const', 'volatile', 'inline', 'unsigned'}

C_KEYWORDS = { 'if', 'else', 'while', 'for', 'return', 'static', 'const', 
                      'break', 'continue', 'goto', 'case', 'default', 'switch', 'enum', 'typedef', 'struct', 'union', 'volatile', 
                      'register', 'auto', 'extern', 'sizeof', 'volatile', 'inline', 'restrict', 'alignas', 'alignof', 
                      'static_assert', 'thread_local'}

C_OPERATORS = {'+', '-', '*', '/', '=', '<', '>', '!', '&', '|', '^', '~', ';', '->', '++', '--', '+=', '-=', '*=', 
               '/=', '%=', '&=', '|=', '^=', '<<=', '>>=', '==', '!=', '<=', '>=', '&&', '||', '<<', '>>', '%', '?', 
               ':', '.', ',', '(', ')', '[', ']', '{', '}'}

class TokenType(Enum):
    KEYWORD = auto()
    IDENTIFIER = auto()
    NUMBER = auto()
    OPERATOR = auto()
    PUNCTUATION = auto()
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
    def __init__(self, code: str):
        self.code: str = code
        self.position: int = 0
        self.line: int = 1
        self.column: int = 1

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
        self.error(f"Unexpected character: {char}")

    def identifier(self) -> Token:
        start: int = self.position
        while self.position < len(self.code) and (self.code[self.position].isalnum() or self.code[self.position] == '_'):
            self.advance()
        value: str = self.code[start:self.position]
        
        if value in C_KEYWORDS:
            return Token(TokenType.KEYWORD, value, self.line, self.column - (self.position - start), self.position)
        return Token(TokenType.IDENTIFIER, value, self.line, self.column - (self.position - start), self.position)

    def number(self) -> Token:
        start: int = self.position
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

        # Check for multi-character operators
        if self.position < len(self.code):
            next_char: str = self.code[self.position]
            potential_op: str = current_op + next_char
            
            if potential_op in C_OPERATORS:
                self.advance()
                current_op = potential_op

                # Check for three-character operators
                if self.position < len(self.code):
                    next_char = self.code[self.position]
                    potential_op = current_op + next_char
                    if potential_op in C_OPERATORS:
                        self.advance()
                        current_op = potential_op

        return Token(TokenType.OPERATOR, current_op, self.line, self.column - len(current_op), self.position)

    def punctuation(self) -> Token:
        value: str = self.code[self.position]
        self.advance()
        return Token(TokenType.PUNCTUATION, value, self.line, self.column - 1, self.position)

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

    def error(self, message: str) -> None:
        raise Exception(f"Lexer error at line {self.line}, column {self.column}: {message}")

class ASTNode:
    def __init__(self, begin_pos: int, end_pos: int):
        self.begin_pos: int = begin_pos
        self.end_pos: int = end_pos

class Program(ASTNode):
    def __init__(self, declarations, comments, begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)
        self.declarations: List[Declaration] = declarations
        self.comments: List[Token] = comments
    
    def __str__(self):
        result = '\n\n'.join(str(decl) for decl in self.declarations)
        if len(self.comments) == 0:
            return result
        lines = result.split('\n')
        comment_index = 0
        for i in range(len(lines)):
            while comment_index < len(self.comments) and self.comments[comment_index].line <= i + 1:
                comment = self.comments[comment_index]
                if comment.type == TokenType.LINE_COMMENT:
                    lines[i] += f" {comment.value}"
                elif comment.type == TokenType.BLOCK_COMMENT:
                    lines[i] += f"\n{comment.value}"
                comment_index += 1
        result = '\n'.join(lines)
        # Add any remaining comments at the end
        while comment_index < len(self.comments):
            result += f"\n{self.comments[comment_index].value}"
            comment_index += 1
        return result

class Declaration(ASTNode):
    def __init__(self, begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)

class Statement(ASTNode):
    def __init__(self, begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)

class Type(ASTNode):
    def __init__(self, name: str, specifiers: List[str], pointer_count: Optional[int], begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)
        self.name: str = name
        self.specifiers: List[str] = specifiers
        self.pointer_count: int = pointer_count

    def __str__(self):
        result = ""
        if len(self.specifiers):
            result += ' '.join(self.specifiers) + ' '
        result += self.name
        if self.pointer_count > 0:
            result += '*' * self.pointer_count
        return result

class CompoundStatement(Statement):
    def __init__(self, statements, begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)
        self.statements: List[Statement] = statements
    
    def __str__(self):
        stmt_strs = '\n'.join('    ' + str(stmt) for stmt in self.statements)
        return f"{{\n{stmt_strs}\n}}"

class Parameter(ASTNode):
    def __init__(self, type: Type, name: str, begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)
        self.type = type
        self.name = name
    
    def __str__(self):
        return f"{self.type} {self.name}"

class FunctionDeclaration(Declaration):
    def __init__(self, return_type: Type, name: str, parameters: List[Parameter], body: Optional[CompoundStatement], begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)
        self.return_type: str = return_type
        self.name: str = name
        self.parameters: List[Parameter] = parameters
        self.body: CompoundStatement = body
    
    def __str__(self):
        params = ', '.join(str(param) for param in self.parameters)
        return f"{self.return_type} {self.name}({params})\n{self.body}"

class Operand(ASTNode):
    def __init__(self, begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)

class ExpressionStatement(Statement):
    def __init__(self, expression: Operand, begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)
        self.expression: Operand = expression
    
    def __str__(self):
        return f"{self.expression};"

class IfStatement(Statement):
    def __init__(self, condition: Operand, then_branch: Statement, else_branch: Optional[Statement], begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)
        self.condition: Operand = condition
        self.then_branch: Statement = then_branch
        self.else_branch: Optional[Statement] = else_branch
    
    def __str__(self):
        if self.else_branch:
            return f"if ({self.condition})\n{self._indent(self.then_branch)}\nelse\n{self._indent(self.else_branch)}"
        return f"if ({self.condition})\n{self._indent(self.then_branch)}"

    def _indent(self, stmt):
        return '\n'.join('    ' + line for line in str(stmt).split('\n'))

class WhileStatement(Statement):
    def __init__(self, condition, body, begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)
        self.condition: Operand = condition
        self.body: Statement = body
    
    def __str__(self):
        return f"while ({self.condition})\n{self._indent(self.body)}"

    def _indent(self, stmt):
        return '\n'.join('    ' + line for line in str(stmt).split('\n'))

class ReturnStatement(Statement):
    def __init__(self, expression, begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)
        self.expression: Optional[Operand] = expression
    
    def __str__(self):
        if self.expression:
            return f"return {self.expression};"
        return "return;"

class BinaryOperation(Operand):
    def __init__(self, left: Operand, operator: Token, right: Operand, begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)
        self.left: Operand = left
        self.operator: str = operator
        self.right: Operand = right
    
    def __str__(self):
        left_str = str(self.left)
        right_str = str(self.right)
        
        if isinstance(self.left, BinaryOperation) and self.__needs_parentheses(self.left):
            left_str = f"({left_str})"
        
        if isinstance(self.right, BinaryOperation) and self.__needs_parentheses(self.right):
            right_str = f"({right_str})"
        
        return f"{left_str} {self.operator} {right_str}"

    def __needs_parentheses(self, child_op):
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

class UnaryOperation(Operand):
    def __init__(self, operator: Token, operand: Operand, begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)
        self.operator: Token = operator
        self.operand: Operand = operand
    
    def __str__(self):
        if isinstance(self.operand, BinaryOperation):
            return f"{self.operator}({self.operand})"
        return f"{self.operator}{self.operand}"

class ArrayAccess(Operand):
    def __init__(self, array: Operand, index: Operand, begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)
        self.array: Operand = array
        self.index: Operand = index
    
    def __str__(self):
        return f"{self.array}[{self.index}]"
    
class MemberAccess(Operand):
    def __init__(self, object: Operand, member: Operand, begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)
        self.object: Operand = object
        self.member: Operand = member
    
    def __str__(self):
        return f"{self.object}.{self.member}"
    
class PointerAccess(Operand):
    def __init__(self, pointer: Operand, member: Operand, begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)
        self.pointer: Operand = pointer
        self.member: Operand = member
    
    def __str__(self):
        return f"{self.pointer}->{self.member}"

class TernaryOperation(Operand):
    def __init__(self, condition: Operand, true_branch: Operand, false_branch: Operand, begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)
        self.condition: Operand = condition
        self.true_branch: Operand = true_branch
        self.false_branch: Operand = false_branch
    
    def __str__(self):
        return f"({self.condition} ? {self.true_branch} : {self.false_branch})"

class Literal(Operand):
    def __init__(self, value: str, begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)
        self.value: str = value
    
    def __str__(self):
        return self.value

class Identifier(Operand):
    def __init__(self, name: str, begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)
        self.name: str = name
    
    def __str__(self):
        return self.name

class FunctionCall(Operand):
    def __init__(self, function: Operand, arguments: List[Operand], begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)
        self.function = function
        self.arguments = arguments
    
    def __str__(self):
        if not len(self.arguments):
            return f"{self.function}()"
        args = ', '.join(str(arg) for arg in self.arguments)
        return f"{self.function}({args})"

class VariableDeclaration(Declaration):
    def __init__(self, type: Type, name: str, initializer: Optional[Operand], begin_pos: int, end_pos: int):
        super().__init__(begin_pos, end_pos)
        self.type: Type = type
        self.name: str = name
        self.initializer: Optional[Operand] = initializer
    
    def __str__(self):
        if self.initializer:
            return f"{self.type} {self.name} = {self.initializer};"
        return f"{self.type} {self.name};"

class ParserException(Exception):
    pass

class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer: Lexer = lexer
        self.current_token: Token = self.lexer.next_token()
        self._rest: str = self.lexer.code[self.lexer.position:]
        self.comments: List[Token] = []

    @property
    def position(self):
        return self.lexer.position
    
    @position.setter
    def position(self, value):
        self.lexer.position = value
        self._rest = self.lexer.code[self.lexer.position:]

    @property
    def _dbg_token(self):
        return (self.current_token.value, self.current_token.type)
    
    def parse(self) -> Program:
        declarations = []
        while self.current_token.type != TokenType.EOF:
            declarations.append(self.parse_statement())
        return Program(declarations, self.comments, 0, self.position)

    def parse_declaration_specifiers(self) -> List[str]:
        specifiers = []
        while self.is_declaration_specifier(self.current_token):
            specifiers.append(self.current_token.value)
            self.advance()
        return specifiers

    def is_declaration_specifier(self, token: Token) -> bool:
        return (token.type == TokenType.KEYWORD and token.value in C_DECLARATION_SPECIFIERS)

    def parse_type(self) -> str:
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
    
    def is_variable_declaration(self) -> bool:
        position = self.position
        current_token = self.current_token
        try:
            self.parse_type()
            self.expect(TokenType.IDENTIFIER) # name
            operator = self.expect(TokenType.OPERATOR)
            return operator.value in ('=', ';')
        except ParserException:
            return False
        finally:
            self.position = position
            self.current_token = current_token

    def is_function_declaration(self) -> bool:
        position = self.position
        current_token = self.current_token
        try:
            _type = self.parse_type()
            _name = self.expect(TokenType.IDENTIFIER)
            self.expect(TokenType.OPERATOR, '(')
            return True
        except ParserException:
            return False
        finally:
            self.position = position
            self.current_token = current_token

    def parse_statement(self) -> Statement:
        start_pos = self.current_token.position
        if self.current_token.type == TokenType.KEYWORD:
            if self.current_token.value == 'if':
                return self.parse_if_statement()
            elif self.current_token.value == 'while':
                return self.parse_while_statement()
            elif self.current_token.value == 'return':
                return self.parse_return_statement()
        elif self.current_token.type == TokenType.OPERATOR and self.current_token.value == '{':
            return self.parse_compound_statement()
        elif self.is_variable_declaration():
            return self.parse_variable_declaration()
        elif self.is_function_declaration():
            return self.parse_function_declaration()
        else:
            return self.parse_expression_statement()

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

    def parse_function_declaration(self) -> FunctionDeclaration:
        start_pos = self.current_token.position
        _type = self.parse_type()
        _name = self.expect(TokenType.IDENTIFIER)
        self.expect(TokenType.OPERATOR, '(')
        parameters = self.parse_parameters()
        self.expect(TokenType.OPERATOR, ')')
        if self.current_token.type == TokenType.OPERATOR and self.current_token.value == ';':
            body = None
            self.advance()
        else:
            body = self.parse_compound_statement()
        return FunctionDeclaration(_type, _name.value, parameters, body, start_pos, self.current_token.position)

    def parse_if_statement(self) -> IfStatement:
        start_pos = self.current_token.position
        self.expect(TokenType.KEYWORD, 'if')
        self.expect(TokenType.OPERATOR, '(')
        condition = self.parse_expression()
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
        return self.parse_logical_or()

    def parse_logical_or(self) -> Operand:
        start_pos = self.current_token.position
        expr = self.parse_logical_and()
        while self.current_token.type == TokenType.OPERATOR and self.current_token.value == '||':
            op = self.current_token.value
            self.advance()
            right = self.parse_logical_and()
            expr = BinaryOperation(expr, op, right, start_pos, self.current_token.position)
        return expr

    def parse_logical_and(self) -> Operand:
        start_pos = self.current_token.position
        expr = self.parse_equality()
        while self.current_token.type == TokenType.OPERATOR and self.current_token.value == '&&':
            op = self.current_token.value
            self.advance()
            right = self.parse_equality()
            expr = BinaryOperation(expr, op, right, start_pos, self.current_token.position)
        return expr

    def parse_equality(self) -> Operand:
        start_pos = self.current_token.position
        expr = self.parse_relational()
        while self.current_token.type == TokenType.OPERATOR and self.current_token.value in ['==', '!=']:
            op = self.current_token.value
            self.advance()
            right = self.parse_relational()
            expr = BinaryOperation(expr, op, right, start_pos, self.current_token.position)
        return expr

    def parse_relational(self) -> Operand:
        start_pos = self.current_token.position
        expr = self.parse_additive()
        while self.current_token.type == TokenType.OPERATOR and self.current_token.value in ['<', '>', '<=', '>=']:
            op = self.current_token.value
            self.advance()
            right = self.parse_additive()
            expr = BinaryOperation(expr, op, right, start_pos, self.current_token.position)
        return expr

    def parse_additive(self) -> Operand:
        start_pos = self.current_token.position
        expr = self.parse_multiplicative()
        while self.current_token.type == TokenType.OPERATOR and self.current_token.value in ['+', '-']:
            op = self.current_token.value
            self.advance()
            right = self.parse_multiplicative()
            expr = BinaryOperation(expr, op, right, start_pos, self.current_token.position)
        return expr

    def parse_multiplicative(self) -> Operand:
        start_pos = self.current_token.position
        expr = self.parse_unary()
        while self.current_token.type == TokenType.OPERATOR and self.current_token.value in ['*', '/', '%']:
            op = self.current_token.value
            self.advance()
            right = self.parse_unary()
            expr = BinaryOperation(expr, op, right, start_pos, self.current_token.position)
        return expr

    def parse_unary(self) -> Operand:
        start_pos = self.current_token.position
        if self.current_token.type == TokenType.OPERATOR and self.current_token.value in ['-', '!', '*', '&', '~']:
            op = self.current_token.value
            self.advance()
            expr = self.parse_unary()
            return UnaryOperation(op, expr, start_pos, self.current_token.position)
        return self.parse_primary()

    def parse_primary(self) -> Operand:
        start_pos = self.current_token.position
        if self.current_token.type == TokenType.NUMBER:
            value = self.current_token.value
            self.advance()
            return Literal(value, start_pos, self.current_token.position)
        elif self.current_token.type == TokenType.IDENTIFIER:
            name = self.current_token.value
            self.advance()
            if self.current_token.type == TokenType.OPERATOR and self.current_token.value == '(':
                return self.parse_function_call(name, start_pos)
            if self.current_token.type == TokenType.OPERATOR and self.current_token.value == '[':
                self.advance()
                expr = self.parse_expression()
                self.expect(TokenType.OPERATOR, ']')
                return ArrayAccess(Identifier(name, start_pos, self.current_token.position), expr, start_pos, self.current_token.position)
            if self.current_token.type == TokenType.OPERATOR and self.current_token.value == '.':
                self.advance()
                expr = self.parse_primary()
                return MemberAccess(Identifier(name, start_pos, self.current_token.position), expr, start_pos, self.current_token.position)
            if self.current_token.type == TokenType.OPERATOR and self.current_token.value == '->':
                self.advance()
                expr = self.parse_primary()
                return PointerAccess(Identifier(name, start_pos, self.current_token.position), expr, start_pos, self.current_token.position)
            return Identifier(name, start_pos, self.current_token.position)
        elif self.current_token.type == TokenType.OPERATOR and self.current_token.value == '(':
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.OPERATOR, ')')
            return expr
        else:
            self.error(f"Unexpected token: {self.current_token}")

    def parse_function_call(self, function_name: str, start_pos: int) -> FunctionCall:
        self.expect(TokenType.OPERATOR, '(')
        arguments = []
        if self.current_token.type != TokenType.OPERATOR or self.current_token.value != ')':
            arguments.append(self.parse_expression())
            while self.current_token.type == TokenType.OPERATOR and self.current_token.value == ',':
                self.advance()
                arguments.append(self.parse_expression())
        self.expect(TokenType.OPERATOR, ')')
        return FunctionCall(Identifier(function_name, start_pos, self.current_token.position), arguments, None, start_pos, self.current_token.position)

    def advance(self):
        self.current_token = self.lexer.next_token()
        while self.current_token.type in (TokenType.LINE_COMMENT, TokenType.BLOCK_COMMENT):
            self.comments.append(self.current_token)
            self.current_token = self.lexer.next_token()
        self.position = self.current_token.position
        self._rest = self.lexer.code[self.position:]


    def expect(self, token_type: TokenType, value: Optional[str] = None) -> Token:
        if self.current_token.type != token_type:
            self.error(f"Expected token type {token_type}, but got {self.current_token.type}")
        if value is not None and self.current_token.value != value:
            self.error(f"Expected token value '{value}', but got '{self.current_token.value}'")
        token = self.current_token
        self.advance()
        return token

    def error(self, message: str):
        raise ParserException(f"Parser error: {message}")

lexer = Lexer("""
void *main() {
    int a = 5 + 5; // eax
    return 0;
}
""")
parser = Parser(lexer)
program = parser.parse()
print(program)