from pydictsql.exceptions import InvalidTokenError
import pytest

from pydictsql.parser import _Parser
from pydictsql.exceptions import UnexpectedTokenError

"""
PARSING TESTS (Covering parsing of SQL)
"""

def test_invalid_start():
    with pytest.raises(UnexpectedTokenError):
        _Parser("WHERE")

def test_invalid_token():
    with pytest.raises(InvalidTokenError):
        _Parser("WRONG")

def test_missing_sql():
    with pytest.raises(UnexpectedTokenError):
        _Parser("")

def test_without_where():
    parser = _Parser("SELECT {val} FROM {source}")
    assert(parser.references.all_references == False)
    assert(parser.references.references == ["{val}"])
    assert(parser.fromref == "{source}")

def test_multiple_references():
    parser = _Parser("SELECT {val1}, {val2},{val3} FROM {source}")
    assert(parser.references.all_references == False)
    assert(parser.references.references == ["{val1}", "{val2}", "{val3}"])
    assert(parser.fromref == "{source}")

def test_select_asterisk():
    parser = _Parser("SELECT * FROM {source}")
    assert(parser.references.all_references)
    assert(parser.references.references == [])
    assert(parser.fromref == "{source}")

def test_single_condition():
    parser = _Parser("SELECT {val1}, {val2},{val3} FROM {source} WHERE {val1} > 1")
    assert(repr(parser.where_clause) == "{val1} > 1")

def test_and_condition():
    parser = _Parser("SELECT {val1}, {val2},{val3} FROM {source} WHERE {val1} > 1 AND {val2} <> 'STRVAL'")
    assert(repr(parser.where_clause) == "{val1} > 1 AND {val2} <> 'STRVAL'")

def test_andor_condition():
    parser = _Parser("SELECT {val1}, {val2},{val3} FROM {source} WHERE {val1} > 1 AND {val2} <> 'STRVAL' OR {val1} = {val3}")
    assert(repr(parser.where_clause) == "{val1} > 1 AND {val2} <> 'STRVAL' OR {val1} = {val3}")

def test_bracketed_condition():
    parser = _Parser("SELECT {val1}, {val2},{val3} FROM {source} WHERE {val1} > 1 AND ({val2} <> 'STRVAL' OR {val1} = {val3})")
    assert(repr(parser.where_clause) == "{val1} > 1 AND ( {val2} <> 'STRVAL' OR {val1} = {val3} )")


"""
EXECUTION TESTS (Covering application of SQL to data)
"""
def test_referencefilter_selected():
    parser = _Parser("SELECT {val1}, {val2},{val3} FROM {source}")
    print(parser.references.references)
    source = {f"val{i}" : f"Value {i}" for i in range(1, 11)}
    expected = {f"val{i}" : f"Value {i}" for i in range(1, 4)}
    assert(parser.references.filter_fields(source) == expected)

def test_referencefilter_all():
    parser = _Parser("SELECT * FROM {source}")
    source = {f"val{i}" : f"Value {i}" for i in range(1, 11)}
    assert(parser.references.filter_fields(source) == source)

def test_simple_where():
    parser = _Parser("SELECT {val1}, {val2},{val3} FROM {source} WHERE {val1} > 1")
    data = [{f"val{i}" : val for i in range(1, 11)} for val in range(0, 4)]
    result = [record for record in data if parser.where_clause.satisfied(record)]
    assert(len(result) == 2)
    for record in result:
        assert(record["val1"] > 1)
