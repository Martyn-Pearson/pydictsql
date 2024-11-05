import pytest

from pydictsql.tokeniser import TokenType, Tokeniser, Token


def test_single_tokens():
    for token, expected in [
        ("SELECT", TokenType.SELECT),
        (",", TokenType.COMMA),
        ("{reference}", TokenType.REFERENCE),
        ("123.45", TokenType.NUMBER),
        ("<", TokenType.LT),
        (">", TokenType.GT),
        ("<=", TokenType.LTE),
        ("<>", TokenType.NE),
    ]:
        tokeniser = Tokeniser(token)
        result = tokeniser.consume()
        assert result.ttype == expected
        assert result.value == token
        assert tokeniser.peek_next() == None
        assert tokeniser.consume() == None

def test_consume_expected():
    tokeniser = Tokeniser("SELECT")
    result = tokeniser.consume(TokenType.SELECT)
    assert result.ttype == TokenType.SELECT

def test_consume_expected_set():
    tokeniser = Tokeniser("SELECT")
    result = tokeniser.consume(set([TokenType.SELECT, TokenType.WHERE]))
    assert result.ttype == TokenType.SELECT

def test_space_separated():
    sql = "SELECT {ref1} , {ref2} FROM {data} WHERE {value1} = 'value' AND {value2} > 13.123"
    expected_types = [
        TokenType.SELECT,
        TokenType.REFERENCE,
        TokenType.COMMA,
        TokenType.REFERENCE,
        TokenType.FROM,
        TokenType.REFERENCE,
        TokenType.WHERE,
        TokenType.REFERENCE,
        TokenType.EQUALS,
        TokenType.STRING,
        TokenType.AND,
        TokenType.REFERENCE,
        TokenType.GT,
        TokenType.NUMBER,
    ]
    expected = [Token(ttype, val) for ttype, val in zip(expected_types, sql.split())]
    tokeniser = Tokeniser(sql)
    for item in expected:
        assert tokeniser.consume() == item
    assert tokeniser.peek_next() == None
    assert tokeniser.consume() == None


def test_realistic_grammar():
    sql = 'SELECT {ref1},{ref2} FROM {data} WHERE {value1}<>"value" OR {value2}<=13123'
    expected = [
        Token(TokenType.SELECT, "SELECT"),
        Token(TokenType.REFERENCE, "{ref1}"),
        Token(TokenType.COMMA, ","),
        Token(TokenType.REFERENCE, "{ref2}"),
        Token(TokenType.FROM, "FROM"),
        Token(TokenType.REFERENCE, "{data}"),
        Token(TokenType.WHERE, "WHERE"),
        Token(TokenType.REFERENCE, "{value1}"),
        Token(TokenType.NE, "<>"),
        Token(TokenType.STRING, '"value"'),
        Token(TokenType.OR, "OR"),
        Token(TokenType.REFERENCE, "{value2}"),
        Token(TokenType.LTE, "<="),
        Token(TokenType.NUMBER, "13123"),
    ]
    tokeniser = Tokeniser(sql)
    for item in expected:
        assert tokeniser.consume() == item
    assert tokeniser.peek_next() == None
    assert tokeniser.consume() == None
