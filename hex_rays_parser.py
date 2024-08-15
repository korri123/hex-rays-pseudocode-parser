from typing import Optional, List, Tuple
from lexer import Lexer, Token, TokenType, MSVC_CALLING_CONVENTIONS, C_DECLARATION_SPECIFIERS
from ast_nodes import *

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

    def parse(self) -> Program:
        declarations = []
        while self.current_token.type != TokenType.EOF:
            declarations.append(self.parse_statement())
        program = Program(declarations, self._comments, 0, self.position)
        self._assign_parents(program)
        return program

    def _assign_parents(self, node: ASTNode):
        for child in node.children():
            child.parent = node
            self._assign_parents(child)

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

    def is_operator(self, operator: str) -> bool:
        return self.current_token.type == TokenType.OPERATOR and self.current_token.value == operator

    def any_of_operators(self, operators: List[str]) -> bool:
        return self.current_token.type == TokenType.OPERATOR and self.current_token.value in operators

    def is_identifier(self, identifier: str) -> bool:
        return self.current_token.type == TokenType.IDENTIFIER and self.current_token.value == identifier
    
    def expect_identifier(self, identifier: str) -> Token:
        return self.expect(TokenType.IDENTIFIER, identifier)
    
    def expect_operator(self, operator: str) -> Token:
        return self.expect(TokenType.OPERATOR, operator)

    def parse_statement(self) -> Statement:
        keyword_handlers = {
            'if': self.parse_if_statement,
            'while': self.parse_while_statement,
            'for': self.parse_for_statement,
            'switch': self.parse_switch_statement,
            'goto': self.parse_goto_statement,
            'return': self.parse_return_statement,
            'break': self.parse_jump_statement,
            'continue': self.parse_jump_statement,
            'case': self.parse_case_statement,
        }
        if self.current_token.value in keyword_handlers:
            return keyword_handlers[self.current_token.value]()
        elif self.is_operator('{'):
            return self.parse_compound_statement()
        elif self.is_variable_declaration():
            return self.parse_variable_declaration()
        elif self.is_function_declaration():
            return self.parse_function_declaration()
        elif self.is_label():
            return self.parse_label_statement()
        else:
            return self.parse_expression_statement()

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
                self.expect_operator('(')
                return True
            except ParserException:
                return False

        return self.with_preserved_position(check)

    def parse_declaration_specifiers(self) -> List[str]:
        specifiers = []
        while self.is_declaration_specifier(self.current_token):
            specifiers.append(self.current_token.value)
            self.advance()
        return specifiers

    def is_declaration_specifier(self, token: Token) -> bool:
        return token.value in C_DECLARATION_SPECIFIERS

    def parse_type(self) -> Type:
        declaration_specifiers = self.parse_declaration_specifiers()
        _type = self.expect(TokenType.IDENTIFIER)
        pointer_count = 0
        while self.is_operator('*'):
            pointer_count += 1
            self.advance()
        return Type(_type.value, declaration_specifiers, pointer_count, _type.position, self.position)

    def parse_parameters(self) -> List[Parameter]:
        parameters = []
        while self.current_token.type != TokenType.OPERATOR or self.current_token.value != ')':
            param_type = self.parse_type()
            param_name = self.expect(TokenType.IDENTIFIER)
            parameters.append(Parameter(param_type, param_name.value, param_type._begin_pos, param_name.position))
            if self.is_operator(','):
                self.advance()
        return parameters

    def parse_compound_statement(self) -> CompoundStatement:
        start_pos = self.current_token.position
        self.expect_operator('{')
        statements = []
        while self.current_token.type != TokenType.OPERATOR or self.current_token.value != '}':
            statements.append(self.parse_statement())
        self.expect_operator('}')
        return CompoundStatement(statements, start_pos, self.current_token.position)

    def parse_return_statement(self) -> ReturnStatement:
        start_pos = self.current_token.position
        self.expect_identifier('return')
        expression = None
        if not self.is_operator(';'):
            expression = self.parse_expression()
        self.expect_operator(';')
        return ReturnStatement(expression, start_pos, self.current_token.position)

    def parse_jump_statement(self) -> JumpStatement:
        start_pos = self.current_token.position
        jump_type = self.current_token.value
        self.advance()
        self.expect_operator(';')
        return JumpStatement(jump_type, start_pos, self.current_token.position)

    def parse_goto_statement(self) -> GotoStatement:
        start_pos = self.current_token.position
        self.expect_identifier('goto')
        label = self.expect(TokenType.IDENTIFIER)
        self.expect_operator(';')
        return GotoStatement(label.value, start_pos, self.current_token.position)

    def is_label(self) -> bool:
        if self.current_token.type != TokenType.IDENTIFIER:
            return False
        next_token = self.lexer.peek_next_token()
        return next_token.type == TokenType.OPERATOR and next_token.value == ':'

    def parse_label_statement(self) -> LabelStatement:
        start_pos = self.current_token.position
        label = self.expect(TokenType.IDENTIFIER)
        self.expect_operator(':')
        return LabelStatement(label.value, start_pos, self.current_token.position)

    def parse_variable_declaration(self) -> VariableDeclaration:
        start_pos = self.current_token.position
        var_type = self.parse_type()
        var_name = self.expect(TokenType.IDENTIFIER)
        initializer = None
        if self.is_operator('='):
            self.advance()
            initializer = self.parse_expression()
        self.expect_operator(';')
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
        self.expect_operator('(')
        parameters = self.parse_parameters()
        self.expect_operator(')')
        if self.is_operator(';'):
            body = None
            self.advance()
        else:
            body = self.parse_compound_statement()
        return FunctionDeclaration(_type, _name.value, parameters, body, calling_convention, start_pos, self.current_token.position)

    def parse_if_statement(self) -> IfStatement:
        start_pos = self.current_token.position
        self.expect_identifier('if')
        self.expect_operator('(')
        condition = self.parse_comma_expression()
        self.expect_operator(')')
        then_branch = self.parse_statement()
        else_branch = None
        if self.is_identifier('else'):
            self.advance()
            else_branch = self.parse_statement()
        return IfStatement(condition, then_branch, else_branch, start_pos, self.current_token.position)

    def parse_while_statement(self) -> WhileStatement:
        start_pos = self.current_token.position
        self.expect_identifier('while')
        self.expect_operator('(')
        condition = self.parse_expression()
        self.expect_operator(')')
        body = self.parse_statement()
        return WhileStatement(condition, body, start_pos, self.current_token.position)

    def parse_for_statement(self) -> ForStatement:
        start_pos = self.current_token.position
        self.expect_identifier('for')
        self.expect_operator('(')
        
        # Parse initializer
        initializer = None
        if not self.is_operator(';'):
            if self.is_variable_declaration():
                initializer = self.parse_variable_declaration()
            else:
                initializer = self.parse_expression_statement()
        else:
            self.advance()  # Skip the semicolon

        # Parse condition
        condition = None
        if not self.is_operator(';'):
            condition = self.parse_expression()
        self.expect_operator(';')

        # Parse increment
        increment = None
        if not self.is_operator(')'):
            increment = self.parse_expression()
        self.expect_operator(')')

        # Parse body
        body = self.parse_statement()

        return ForStatement(initializer, condition, increment, body, start_pos, self.current_token.position)

    def parse_function_call(self, function: Operand, start_pos: int) -> FunctionCall:
        self.expect_operator('(')
        arguments = []
        if not self.is_operator(')'):
            arguments.append(self.parse_expression())
            while self.is_operator(','):
                self.advance()
                arguments.append(self.parse_argument())
        self.expect_operator(')')
        return FunctionCall(function, arguments, start_pos, self.current_token.position)

    def parse_switch_statement(self) -> SwitchStatement:
        start_pos = self.current_token.position
        self.expect_identifier('switch')
        self.expect_operator('(')
        expression = self.parse_expression()
        self.expect_operator(')')
        self.expect_operator('{')
        cases = []
        while not self.is_operator('}'):
            cases.append(self.parse_case_statement())
        self.expect_operator('}')
        return SwitchStatement(expression, cases, start_pos, self.current_token.position)
    
    def parse_case_statement(self) -> CaseStatement:
        start_pos = self.current_token.position
        if self.is_identifier('case'):
            self.advance()
            value = self.parse_expression()
            self.expect_operator(':')
        elif self.is_identifier('default'):
            self.advance()
            self.expect_operator(':')
            value = None
        else:
            raise self.error("Expected 'case' or 'default'")
        
        statements = []
        while not (self.is_identifier('case') or self.is_identifier('default') or self.is_operator('}')):
            statements.append(self.parse_statement())
        
        return CaseStatement(value, statements, start_pos, self.current_token.position)

    def parse_expression_statement(self) -> ExpressionStatement:
        start_pos = self.current_token.position
        expression = self.parse_expression()
        self.expect_operator(';')
        return ExpressionStatement(expression, start_pos, self.current_token.position)

    def parse_expression(self) -> Operand:
        return self.parse_comma_expression()

    def parse_comma_expression(self) -> Operand:
        start_pos = self.current_token.position
        expr = self.parse_assignment()
        if self.is_operator(','):
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
        if self.any_of_operators(['=', '+=', '-=', '*=', '/=', '%=', '&=', '|=', '^=', '<<=', '>>=']):
            op = self.current_token
            self.advance()
            right = self.parse_assignment()
            return BinaryOperation(left, op.value, right, start_pos, self.current_token.position)
        return left

    def parse_logical_or(self) -> Operand:
        start_pos = self.current_token.position
        expr = self.parse_logical_and()
        while self.is_operator('||'):
            op = self.current_token
            self.advance()
            right = self.parse_logical_and()
            expr = BinaryOperation(expr, op.value, right, start_pos, self.current_token.position)
        return expr

    def parse_logical_and(self) -> Operand:
        start_pos = self.current_token.position
        expr = self.parse_bitwise_or()
        while self.is_operator('&&'):
            op = self.current_token
            self.advance()
            right = self.parse_bitwise_or()
            expr = BinaryOperation(expr, op.value, right, start_pos, self.current_token.position)
        return expr
    
    def parse_bitwise_or(self) -> Operand:
        start_pos = self.current_token.position
        expr = self.parse_bitwise_xor()
        while self.is_operator('|'):
            op = self.current_token
            self.advance()
            right = self.parse_bitwise_xor()
            expr = BinaryOperation(expr, op.value, right, start_pos, self.current_token.position)
        return expr

    def parse_bitwise_xor(self) -> Operand:
        start_pos = self.current_token.position
        expr = self.parse_bitwise_and()
        while self.is_operator('^'):
            op = self.current_token
            self.advance()
            right = self.parse_bitwise_and()
            expr = BinaryOperation(expr, op.value, right, start_pos, self.current_token.position)
        return expr

    def parse_bitwise_and(self) -> Operand:
        start_pos = self.current_token.position
        expr = self.parse_equality()
        while self.is_operator('&'):
            op = self.current_token
            self.advance()
            right = self.parse_equality()
            expr = BinaryOperation(expr, op.value, right, start_pos, self.current_token.position)
        return expr

    def parse_equality(self) -> Operand:
        start_pos = self.current_token.position
        expr = self.parse_relational()
        while self.any_of_operators(['==', '!=']):
            op = self.current_token
            self.advance()
            right = self.parse_relational()
            expr = BinaryOperation(expr, op.value, right, start_pos, self.current_token.position)
        return expr

    def parse_relational(self) -> Operand:
        start_pos = self.current_token.position
        expr = self.parse_additive()
        while self.any_of_operators(['<', '>', '<=', '>=']):
            op = self.current_token
            self.advance()
            right = self.parse_additive()
            expr = BinaryOperation(expr, op.value, right, start_pos, self.current_token.position)
        return expr

    def parse_additive(self) -> Operand:
        start_pos = self.current_token.position
        expr = self.parse_multiplicative()
        while self.any_of_operators(['+', '-']):
            op = self.current_token
            self.advance()
            right = self.parse_multiplicative()
            expr = BinaryOperation(expr, op.value, right, start_pos, self.current_token.position)
        return expr

    def parse_multiplicative(self) -> Operand:
        start_pos = self.current_token.position
        expr = self.parse_unary()
        while self.any_of_operators(['*', '/', '%']):
            op = self.current_token
            self.advance()
            right = self.parse_unary()
            expr = BinaryOperation(expr, op.value, right, start_pos, self.current_token.position)
        return expr

    def parse_unary(self) -> Operand:
        start_pos = self.current_token.position
        if self.any_of_operators(['-', '!', '*', '&', '~', '++', '--']):
            op = self.current_token
            self.advance()
            expr = self.parse_unary()
            return UnaryOperation(op.value, expr, False, start_pos, self.current_token.position)
        return self.parse_postfix()

    def parse_postfix(self) -> Operand:
        expr = self.parse_primary()
        start_pos = expr._begin_pos

        while self.current_token.type == TokenType.OPERATOR:
            if self.any_of_operators(['++', '--']):
                op = self.current_token
                self.advance()
                expr = UnaryOperation(op.value, expr, True, start_pos, self.current_token.position)
            elif self.is_operator('('):
                expr = self.parse_function_call(expr, start_pos)
            elif self.is_operator('['):
                self.advance()
                index = self.parse_expression()
                self.expect_operator(']')
                expr = ArrayAccess(expr, index, start_pos, self.current_token.position)
            elif self.is_operator('.'):
                self.advance()
                member = self.parse_primary()
                expr = MemberAccess(expr, member, start_pos, self.current_token.position)
            elif self.is_operator('->'):
                self.advance()
                member = self.parse_primary()
                expr = PointerAccess(expr, member, start_pos, self.current_token.position)
            else:
                break

        return expr

    def parse_primary(self) -> Operand:
        start_pos = self.current_token.position
        expr = None

        if self.current_token.type == TokenType.NUMBER:
            value = self.current_token.value
            self.advance()
            expr = Literal(value, start_pos, self.current_token.position)
        elif self.current_token.type == TokenType.IDENTIFIER:
            name = self.current_token.value
            self.advance()
            expr = Identifier(name, start_pos, self.current_token.position)
        elif self.is_operator('('):
            self.advance()
            expr = self.parse_expression()
            self.expect_operator(')')
        elif self.current_token.type == TokenType.STRING:
            value = self.current_token.value
            self.advance()
            expr = StringLiteral(value, start_pos, self.current_token.position)
        else:
            raise self.error(f"Unexpected token: {self.current_token}")

        return expr
