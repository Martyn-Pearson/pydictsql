import pytest

from pydictsql.tokeniser import TokenType, Tokeniser

def test_tokentype_keywords():
    for val, expected in [
        # Keywords
        ("SELECT", TokenType.SELECT),
        ("FROM", TokenType.FROM),
        ("WHERE", TokenType.WHERE),
        ("AND", TokenType.AND),
        ("OR", TokenType.OR),

        # Lower / mixed case keywords
        ("select", TokenType.SELECT),
        ("From", TokenType.FROM),
       ]:
        assert(TokenType.get_token(val) == expected)

def test_tokentype_references():
        for val in ["{reference}",
                    "{1}",
                    "{ref_with_underscore}",
                    "{_underscore_start}",
                    "{select}",
                    "{From}",
                    ]:
            assert(TokenType.get_token(val) == TokenType.REFERENCE)


def test_tokentype_numbers():
     for val in ["1",
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
          assert(TokenType.get_token(val) == TokenType.NUMBER)
          
def test_tokentype_strings():
     for val in ["'asas'", '"asas"']:
          assert(TokenType.get_token(val) == TokenType.STRING)

def test_tokentype_operators():
     for val, expected in [("=", TokenType.EQUALS),
                                ("<", TokenType.LT),
                                (">", TokenType.GT),
                                ("(", TokenType.LPAREN),
                                (")", TokenType.RPAREN),
     ]:
          assert(TokenType.get_token(val) == expected)

def test_tokentype_invalid():
     for val in ["1dc", "?", "$", "'unfinished", '"unfinished']:
          assert(TokenType.get_token(val) == None)
 