from .tokeniser import Tokeniser, TokenType, UnexpectedTokenException

"""
Supported grammar:
Statement ::= SELECT <References> FROM REFERENCE [WHERE <Where_Clause>]
References ::= REFERENCE | REFERENCE COMMA References
Where_Clause ::= <Where_Term> [OR Where_Clause]
Where_Term ::= <Where_Factor> [AND <Where_Term>]
Where_Factor ::= <Where_Primary> | NOT <Where_Primary>
Where_Primary ::= LPAREN Where_Clause RPAREN | Condition
Condition ::= REFERENCE COMPARATOR <RValue>
RValue ::= REFERENCE | NUMBER | STRING
"""

class Condition:
    """
    Constructs a condition container as per the grammar above
    """
    def __init__(self):
        self.reference = None
        self.operator = None
        self.rvalue = None

    def parse(self, tokeniser):
        self.reference = tokeniser.consume(TokenType.REFERENCE).value
        self.operator = tokeniser.consume(TokenType.comparators())
        self.rvalue = tokeniser.consume(TokenType.rvalues())

    def __repr__(self):
        if self.reference and self.operator and self.rvalue:
            return " ".join([self.reference, self.operator.value, self.rvalue.value])
        return "Empty / invalid condition"

class WherePrimary:
    """
    Constructs a where primary container as per the grammar above
    """
    def __init__(self):
        self.where_clause = None
        self.condition = None

    def parse(self, tokeniser):
        if tokeniser.next_is(TokenType.LPAREN):
            tokeniser.consume(TokenType.LPAREN)
            self.where_clause = WhereClause()
            self.where_clause.parse(tokeniser)
            tokeniser.consume(TokenType.RPAREN)
        else:
            self.condition = Condition()
            self.condition.parse(tokeniser)

    def __repr__(self):
        if self.where_clause:
            return "( " + repr(self.where_clause) + " )"
        else:
            return repr(self.condition)

class WhereFactor:
    """
    Constructs a where factor container as per the grammar above
    """
    def __init__(self):
        self.where_primary = WherePrimary()
        self.bool_not = False

    def parse(self, tokeniser):
        if tokeniser.next_is(TokenType.NOT):
            tokeniser.consume(TokenType.NOT)
            self.bool_not = True
        self.where_primary.parse(tokeniser)

    def __repr__(self):
        return ("NOT " if self.bool_not else "") + repr(self.where_primary)

class WhereTerm:
    """
    Constructs a where term container as per the grammar above
    """
    def __init__(self):
        self.where_factor = WhereFactor()
        self.where_term = None

    def parse(self, tokeniser):
        self.where_factor.parse(tokeniser)
        if tokeniser.next_is(TokenType.AND):
            tokeniser.consume(TokenType.AND)
            self.where_term = WhereTerm()
            self.where_term.parse(tokeniser)

    def __repr__(self):
        return repr(self.where_factor) + (" AND " + repr(self.where_term) if self.where_term else "")

class WhereClause:
    """
    Constructs a where clause container as per the grammar above
    """
    def __init__(self):
        self.where_term = WhereTerm()
        self.where_clause = None

    def parse(self, tokeniser):
        self.where_term.parse(tokeniser)
        if tokeniser.next_is(TokenType.OR):
            tokeniser.consume(TokenType.OR)
            self.where_clause = WhereClause()
            self.where_clause.parse(tokeniser)

    def __repr__(self):
        return repr(self.where_term) + (" OR " + repr(self.where_clause) if self.where_clause else "")

class Parser:
    """
    Constructs a parser and parses the given SQL, storing the reference and conditions to be used when querying data
    :param sql: SQL to be parsed
    :raises InvalidTokenException: Raised (by the tokeniser) if an invalid token is read
    :raises UnexpectedTokenException: Raised when parsing we hit a token which does not match expected type
    """

    def __init__(self, sql: str):
        self.tokeniser = Tokeniser(sql)
        # Because references and fromref are straightforward, we store them directly here, but as the 
        # where clause hierarchy is more complex, that is stored in child objects
        self.references = [] 
        self.fromref = ""
        self.where_clause = None
        self._parse()

    def _parse(self):
        self.tokeniser.consume(TokenType.SELECT)
        self._parse_references()
        self.tokeniser.consume(TokenType.FROM)
        self.fromref = self.tokeniser.consume(TokenType.REFERENCE).value
        if self.tokeniser.next_is(TokenType.WHERE):
            self.tokeniser.consume(TokenType.WHERE)
            self._parse_where_clause()
        if not self.tokeniser.peek_next() is None:
            raise UnexpectedTokenException(self.tokeniser.peek_next())

    def _parse_references(self):
        self.references.append(self.tokeniser.consume(TokenType.REFERENCE).value)
        while self.tokeniser.next_is(TokenType.COMMA):
            self.tokeniser.consume(TokenType.COMMA)
            self.references.append(self.tokeniser.consume(TokenType.REFERENCE).value)

    def _parse_where_clause(self):
        self.where_clause = WhereClause()
        self.where_clause.parse(self.tokeniser)

