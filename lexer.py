from typing import Optional
from enum import Enum, auto

MSVC_CALLING_CONVENTIONS = {'__stdcall', '__cdecl', '__fastcall', '__thiscall', '__vectorcall'}
C_DECLARATION_SPECIFIERS = {'static', 'extern', 'auto', 'register', 'const', 'volatile', 'inline', 'unsigned', 'thread_local'}

C_OPERATORS = {'+', '-', '*', '/', '=', '<', '>', '!', '&', '|', '^', '~', ';', '->', '++', '--', '+=', '-=', '*=', 
               '/=', '%=', '&=', '|=', '^=', '<<=', '>>=', '==', '!=', '<=', '>=', '&&', '||', '<<', '>>', '%', '?', 
               ':', '.', ',', '(', ')', '[', ']', '{', '}'}
# Add the '::' operator to the list of C operators since it can be in the function name in pseudocode
C_OPERATORS |= {'::'}

class TokenType(Enum):
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
            # Decimal or octal number
            while self.position < len(self.code) and self.code[self.position].isdigit():
                self.advance()
            if self.position < len(self.code) and self.code[self.position] == '.':
                self.advance()
                while self.position < len(self.code) and self.code[self.position].isdigit():
                    self.advance()
            # Handle exponent part
            if self.position < len(self.code) and self.code[self.position].lower() == 'e':
                self.advance()
                if self.position < len(self.code) and self.code[self.position] in '+-':
                    self.advance()
                while self.position < len(self.code) and self.code[self.position].isdigit():
                    self.advance()

        # Handle suffixes
        while self.position < len(self.code) and self.code[self.position].lower() in 'ulfi':
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
