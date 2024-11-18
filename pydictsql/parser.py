from .exceptions import UnexpectedTokenError, UnrecognisedReferenceError
from .tokeniser import _Tokeniser, _TokenType

"""
Supported grammar:
Statement ::= SELECT <References> FROM REFERENCE [WHERE <Where_Clause>]
References ::= ASTERISK | ReferenceList
ReferenceList ::= REFERENCE | REFERENCE COMMA ReferenceList
Where_Clause ::= <Where_Term> [OR Where_Clause]
Where_Term ::= <Where_Factor> [AND <Where_Term>]
Where_Factor ::= <Where_Primary> | NOT <Where_Primary>
Where_Primary ::= LPAREN Where_Clause RPAREN | Condition
Condition ::= REFERENCE COMPARATOR <RValue>
RValue ::= REFERENCE | NUMBER | STRING
"""


def clean_outers(reference):
    # Removes outer curly brackets or quotes from a value
    return reference[1:-1]


class _References:
    def __init__(self):
        self.all_references = False
        self.references = []

    def parse(self, tokeniser):
        if tokeniser.next_is(_TokenType.ASTERISK):
            tokeniser.consume(_TokenType.ASTERISK)
            self.all_references = True
        else:
            self.references.append(tokeniser.consume(_TokenType.REFERENCE).value)
            while tokeniser.next_is(_TokenType.COMMA):
                tokeniser.consume(_TokenType.COMMA)
                self.references.append(tokeniser.consume(_TokenType.REFERENCE).value)

    def filter_fields(self, record):
        if self.all_references:
            return record
        return {key: record[key] for key in map(clean_outers, self.references)}


class _Condition:
    """
    Constructs a condition container as per the grammar above
    """

    def __init__(self):
        self.reference = None
        self.operator = None
        self.rvalue = None

    def parse(self, tokeniser):
        self.reference = tokeniser.consume(_TokenType.REFERENCE).value
        self.operator = tokeniser.consume(_TokenType.comparators())
        self.rvalue = tokeniser.consume(_TokenType.rvalues())

    def __repr__(self):
        return " ".join([self.reference, self.operator.value, self.rvalue.value])

    def satisfied(self, record):
        _Condition._validate_reference(self.reference, record)
        if self.rvalue.ttype == _TokenType.REFERENCE:
            _Condition._validate_reference(self.rvalue.value, record)
        lvalue = record[clean_outers(self.reference)]
        match self.rvalue.ttype:
            case _TokenType.REFERENCE:
                rvalue = record[clean_outers(self.rvalue.value)]
            case _TokenType.STRING:
                rvalue = clean_outers(self.rvalue.value)
            case _:
                rvalue = self.rvalue.value
        if not isinstance(lvalue, str):
            rvalue = type(lvalue)(rvalue)

        match self.operator.ttype:
            case _TokenType.LT:
                return lvalue < rvalue
            case _TokenType.LTE:
                return lvalue <= rvalue
            case _TokenType.GT:
                return lvalue > rvalue
            case _TokenType.GTE:
                return lvalue >= rvalue
            case _TokenType.EQUALS:
                return lvalue == rvalue
            case _TokenType.NE:
                return lvalue != rvalue

    @staticmethod
    def _validate_reference(reference, record):
        if not clean_outers(reference) in record:
            raise UnrecognisedReferenceError(reference)


class _WherePrimary:
    """
    Constructs a where primary container as per the grammar above
    """

    def __init__(self):
        self.where_clause = None
        self.condition = None

    def parse(self, tokeniser):
        if tokeniser.next_is(_TokenType.LPAREN):
            tokeniser.consume(_TokenType.LPAREN)
            self.where_clause = _WhereClause()
            self.where_clause.parse(tokeniser)
            tokeniser.consume(_TokenType.RPAREN)
        else:
            self.condition = _Condition()
            self.condition.parse(tokeniser)

    def __repr__(self):
        if self.where_clause:
            return "( " + repr(self.where_clause) + " )"
        else:
            return repr(self.condition)

    def satisfied(self, record):
        if self.where_clause:
            return self.where_clause.satisfied(record)
        else:
            return self.condition.satisfied(record)


class _WhereFactor:
    """
    Constructs a where factor container as per the grammar above
    """

    def __init__(self):
        self.where_primary = _WherePrimary()
        self.bool_not = False

    def parse(self, tokeniser):
        if tokeniser.next_is(_TokenType.NOT):
            tokeniser.consume(_TokenType.NOT)
            self.bool_not = True
        self.where_primary.parse(tokeniser)

    def __repr__(self):
        return ("NOT " if self.bool_not else "") + repr(self.where_primary)

    def satisfied(self, record):
        return self.where_primary.satisfied(record) ^ self.bool_not


class _WhereTerm:
    """
    Constructs a where term container as per the grammar above
    """

    def __init__(self):
        self.where_factor = _WhereFactor()
        self.where_term = None

    def parse(self, tokeniser):
        self.where_factor.parse(tokeniser)
        if tokeniser.next_is(_TokenType.AND):
            tokeniser.consume(_TokenType.AND)
            self.where_term = _WhereTerm()
            self.where_term.parse(tokeniser)

    def __repr__(self):
        return repr(self.where_factor) + (
            " AND " + repr(self.where_term) if self.where_term else ""
        )

    def satisfied(self, record):
        return self.where_factor.satisfied(record) and (
            self.where_term is None or self.where_term.satisfied(record)
        )


class _WhereClause:
    """
    Constructs a where clause container as per the grammar above
    """

    def __init__(self):
        self.where_term = _WhereTerm()
        self.where_clause = None

    def parse(self, tokeniser):
        self.where_term.parse(tokeniser)
        if tokeniser.next_is(_TokenType.OR):
            tokeniser.consume(_TokenType.OR)
            self.where_clause = _WhereClause()
            self.where_clause.parse(tokeniser)

    def __repr__(self):
        return repr(self.where_term) + (
            " OR " + repr(self.where_clause) if self.where_clause else ""
        )

    def satisfied(self, record):
        return self.where_term.satisfied(record) or (
            self.where_clause is not None and self.where_clause.satisfied(record)
        )


class _Parser:
    """
    Constructs a parser and parses the given SQL, storing the reference and conditions to be used when querying data
    :param sql: SQL to be parsed
    :raises InvalidTokenError: Raised (by the tokeniser) if an invalid token is read
    :raises UnexpectedTokenError: Raised when parsing we hit a token which does not match expected type
    """

    def __init__(self, sql: str):
        self.tokeniser = _Tokeniser(sql)
        # Because references and fromref are straightforward, we store them directly here, but as the
        # where clause hierarchy is more complex, that is stored in child objects
        self._references = _References()
        self._fromref = ""
        self._where_clause = None
        self._parse()

    def satisfied(self, record):
        return (
            True if self._where_clause is None else self._where_clause.satisfied(record)
        )

    def filter_fields(self, record):
        return self._references.filter_fields(record)

    def from_ref(self):
        return clean_outers(self._fromref)

    def _parse(self):
        self.tokeniser.consume(_TokenType.SELECT)
        self._parse_references()
        self.tokeniser.consume(_TokenType.FROM)
        self._fromref = self.tokeniser.consume(_TokenType.REFERENCE).value
        if self.tokeniser.next_is(_TokenType.WHERE):
            self.tokeniser.consume(_TokenType.WHERE)
            self._parse_where_clause()
        if not self.tokeniser.peek_next() is None:
            raise UnexpectedTokenError(self.tokeniser.peek_next())

    def _parse_references(self):
        self._references.parse(self.tokeniser)

    def _parse_where_clause(self):
        self._where_clause = _WhereClause()
        self._where_clause.parse(self.tokeniser)
