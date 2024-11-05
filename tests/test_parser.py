import pytest

from pydictsql.parser import Parser
from pydictsql.tokeniser import UnexpectedTokenException, InvalidTokenException

def test_invalid_start():
    with pytest.raises(UnexpectedTokenException):
        Parser("WHERE")

def test_invalid_token():
    with pytest.raises(InvalidTokenException):
        Parser("WRONG")

def test_missing_sql():
    with pytest.raises(UnexpectedTokenException):
        Parser("")

def test_without_where():
    parser = Parser("SELECT {val} FROM {source}")
    assert(parser.references == ["{val}"])
    assert(parser.fromref == "{source}")

def test_multiple_references():
    parser = Parser("SELECT {val1}, {val2},{val3} FROM {source}")
    assert(parser.references == ["{val1}", "{val2}", "{val3}"])
    assert(parser.fromref == "{source}")

def test_single_condition():
    parser = Parser("SELECT {val1}, {val2},{val3} FROM {source} WHERE {val1} > 1")

def test_and_condition():
    parser = Parser("SELECT {val1}, {val2},{val3} FROM {source} WHERE {val1} > 1 AND {val2} <> 'STRVAL'")

def test_and_condition():
    parser = Parser("SELECT {val1}, {val2},{val3} FROM {source} WHERE {val1} > 1 AND {val2} <> 'STRVAL'")

def test_andor_condition():
    parser = Parser("SELECT {val1}, {val2},{val3} FROM {source} WHERE {val1} > 1 AND {val2} <> 'STRVAL' OR {val1} = {val3}")
