import pytest

from pydictsql.tokeniser import _TokenType, _Tokeniser, _Token


def test_single_tokens():
    for token, expected in [
        ("SELECT", _TokenType.SELECT),
        (",", _TokenType.COMMA),
        ("{reference}", _TokenType.REFERENCE),
        ("123.45", _TokenType.NUMBER),
        ("<", _TokenType.LT),
        (">", _TokenType.GT),
        ("<=", _TokenType.LTE),
        ("<>", _TokenType.NE),
        ("*", _TokenType.ASTERISK),
    ]:
        tokeniser = _Tokeniser(token)
        result = tokeniser.consume()
        assert result.ttype == expected
        assert result.value == token
        assert tokeniser.peek_next() == None
        assert tokeniser.consume() == None


def test_consume_expected():
    tokeniser = _Tokeniser("SELECT")
    result = tokeniser.consume(_TokenType.SELECT)
    assert result.ttype == _TokenType.SELECT


def test_consume_expected_set():
    tokeniser = _Tokeniser("SELECT")
    result = tokeniser.consume(set([_TokenType.SELECT, _TokenType.WHERE]))
    assert result.ttype == _TokenType.SELECT


def test_space_separated():
    sql = "SELECT {ref1} , {ref2} FROM {data} WHERE {value1} = 'value' AND {value2} > 13.123"
    expected_types = [
        _TokenType.SELECT,
        _TokenType.REFERENCE,
        _TokenType.COMMA,
        _TokenType.REFERENCE,
        _TokenType.FROM,
        _TokenType.REFERENCE,
        _TokenType.WHERE,
        _TokenType.REFERENCE,
        _TokenType.EQUALS,
        _TokenType.STRING,
        _TokenType.AND,
        _TokenType.REFERENCE,
        _TokenType.GT,
        _TokenType.NUMBER,
    ]
    expected = [_Token(ttype, val) for ttype, val in zip(expected_types, sql.split())]
    tokeniser = _Tokeniser(sql)
    for item in expected:
        assert tokeniser.consume() == item
    assert tokeniser.peek_next() == None
    assert tokeniser.consume() == None


def test_realistic_grammar():
    sql = 'SELECT {ref1},{ref2} FROM {data} WHERE {value1}<>"value" OR {value2}<=13123'
    expected = [
        _Token(_TokenType.SELECT, "SELECT"),
        _Token(_TokenType.REFERENCE, "{ref1}"),
        _Token(_TokenType.COMMA, ","),
        _Token(_TokenType.REFERENCE, "{ref2}"),
        _Token(_TokenType.FROM, "FROM"),
        _Token(_TokenType.REFERENCE, "{data}"),
        _Token(_TokenType.WHERE, "WHERE"),
        _Token(_TokenType.REFERENCE, "{value1}"),
        _Token(_TokenType.NE, "<>"),
        _Token(_TokenType.STRING, '"value"'),
        _Token(_TokenType.OR, "OR"),
        _Token(_TokenType.REFERENCE, "{value2}"),
        _Token(_TokenType.LTE, "<="),
        _Token(_TokenType.NUMBER, "13123"),
    ]
    tokeniser = _Tokeniser(sql)
    for item in expected:
        assert tokeniser.consume() == item
    assert tokeniser.peek_next() == None
    assert tokeniser.consume() == None
