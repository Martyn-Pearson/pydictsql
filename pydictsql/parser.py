from .tokeniser import Tokeniser, TokenType, UnexpectedTokenException

"""
Supported grammar:
Statement ::= SELECT <References> FROM REFERENCE <Where_Clause>
References ::= REFERENCE | REFERENCE COMMA References
Where_Clause ::=  | WHERE <Conditions>
Conditions ::= Expression | Expression LOGICOP Conditions
Expression ::= LPAREN Conditions RPAREN | Condition
Condition ::= REFERENCE OPERATOR <RValue>
RValue ::= REFERENCE | NUMBER | STRING
"""


class Parser:
    """
    Constructs a parser and parses the given SQL, storing the reference and conditions to be used when querying data
    :param sql: SQL to be parsed
    :raises InvalidTokenException: Raised (by the tokeniser) if an invalid token is read
    :raises UnexpectedTokenException: Raised when parsing we hit a token which does not match expected type
    """

    def __init__(self, sql: str):
        self.tokeniser = Tokeniser(sql)
        self.references = []
        self.fromref = ""
        self._parse()

    def _parse(self):
        self.tokeniser.consume(TokenType.SELECT)
        self._parse_references()
        self.tokeniser.consume(TokenType.FROM)
        self.fromref = self.tokeniser.consume(TokenType.REFERENCE).value
        if self.tokeniser.next_is(TokenType.WHERE):
            self.tokeniser.consume(TokenType.WHERE)
            self._parse_conditions()
        if not self.tokeniser.peek_next() is None:
            raise UnexpectedTokenException(self.tokeniser.peek_next())

    def _parse_references(self):
        self.references.append(self.tokeniser.consume(TokenType.REFERENCE).value)
        while self.tokeniser.next_is(TokenType.COMMA):
            self.tokeniser.consume(TokenType.COMMA)
            self.references.append(self.tokeniser.consume(TokenType.REFERENCE).value)

    def _parse_expression(self):
        if self.tokeniser.next_is(TokenType.LPAREN):
            self.tokeniser.consume(TokenType.LPAREN)
            self._parse_conditions()
            self.tokeniser.consume(TokenType.RPAREN)
        else:
            self._parse_condition()

    def _parse_conditions(self):
        self._parse_expression()
        next = self.tokeniser.peek_next()
        if next and TokenType.is_logic_op(next.ttype):
            op = self.tokeniser.consume(TokenType.logic_ops())
            self._parse_conditions()
        
    def _parse_condition(self):
        self.tokeniser.consume(TokenType.REFERENCE)
        self.tokeniser.consume(TokenType.comparators())
        self.tokeniser.consume(TokenType.rvalues())

