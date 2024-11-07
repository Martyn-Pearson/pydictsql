import pytest

from pydictsql.tokeniser import _TokenType


def test_tokentype_keywords():
    for val, expected in [
        # Keywords
        ("SELECT", _TokenType.SELECT),
        ("FROM", _TokenType.FROM),
        ("WHERE", _TokenType.WHERE),
        ("AND", _TokenType.AND),
        ("OR", _TokenType.OR),
        ("NOT", _TokenType.NOT),
        # Lower / mixed case keywords
        ("select", _TokenType.SELECT),
        ("From", _TokenType.FROM),
    ]:
        assert _TokenType.get_token(val) == expected


def test_tokentype_references():
    for val in [
        "{reference}",
        "{1}",
        "{ref_with_underscore}",
        "{_underscore_start}",
        "{select}",
        "{From}",
    ]:
        assert _TokenType.get_token(val) == _TokenType.REFERENCE


def test_tokentype_numbers():
    for val in [
        "1",
        "100",
        "-1",
        "-1000",
        "1.2",
        "1.21",
        "11.2",
        "11.21",
        "-1.2",
        "-1.21",
        "-11.2",
        "-11.21",
    ]:
        assert _TokenType.get_token(val) == _TokenType.NUMBER


def test_tokentype_strings():
    for val in ["'asas'", '"asas"']:
        assert _TokenType.get_token(val) == _TokenType.STRING


def test_tokentype_operators():
    for val, expected in [
        ("=", _TokenType.EQUALS),
        ("<", _TokenType.LT),
        ("<=", _TokenType.LTE),
        (">", _TokenType.GT),
        (">=", _TokenType.GTE),
        ("<>", _TokenType.NE),
        ("(", _TokenType.LPAREN),
        (")", _TokenType.RPAREN),
        (",", _TokenType.COMMA),
        ("*", _TokenType.ASTERISK),
    ]:
        assert _TokenType.get_token(val) == expected


def test_tokentype_invalid():
    for val in ["1dc", "?", "$", "'unfinished", '"unfinished']:
        assert _TokenType.get_token(val) == None
