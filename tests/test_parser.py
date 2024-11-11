import pytest

from pydictsql.parser import _Parser
from pydictsql.exceptions import UnexpectedTokenError, UnrecognisedReferenceError, InvalidTokenError

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
    assert(parser._references.all_references == False)
    assert(parser._references.references == ["{val}"])
    assert(parser._fromref == "{source}")

def test_multiple_references():
    parser = _Parser("SELECT {val1}, {val2},{val3} FROM {source}")
    assert(parser._references.all_references == False)
    assert(parser._references.references == ["{val1}", "{val2}", "{val3}"])
    assert(parser._fromref == "{source}")

def test_select_asterisk():
    parser = _Parser("SELECT * FROM {source}")
    assert(parser._references.all_references)
    assert(parser._references.references == [])
    assert(parser._fromref == "{source}")

def test_single_condition():
    parser = _Parser("SELECT {val1}, {val2},{val3} FROM {source} WHERE {val1} > 1")
    assert(repr(parser._where_clause) == "{val1} > 1")

def test_and_condition():
    parser = _Parser("SELECT {val1}, {val2},{val3} FROM {source} WHERE {val1} > 1 AND {val2} <> 'STRVAL'")
    assert(repr(parser._where_clause) == "{val1} > 1 AND {val2} <> 'STRVAL'")

def test_andor_condition():
    parser = _Parser("SELECT {val1}, {val2},{val3} FROM {source} WHERE {val1} > 1 AND {val2} <> 'STRVAL' OR {val1} = {val3}")
    assert(repr(parser._where_clause) == "{val1} > 1 AND {val2} <> 'STRVAL' OR {val1} = {val3}")

def test_bracketed_condition():
    parser = _Parser("SELECT {val1}, {val2},{val3} FROM {source} WHERE {val1} > 1 AND ({val2} <> 'STRVAL' OR {val1} = {val3})")
    assert(repr(parser._where_clause) == "{val1} > 1 AND ( {val2} <> 'STRVAL' OR {val1} = {val3} )")

def test_extraneous_terms():
    with pytest.raises(UnexpectedTokenError):
        parser = _Parser("SELECT {val1}, {val2},{val3} FROM {source} WHERE {val1} > 1 AND ({val2} <> 'STRVAL' OR {val1} = {val3}) SELECT")

def test_unfinished():
    with pytest.raises(UnexpectedTokenError):
        parser = _Parser("SELECT {val1}, {val2},{val3} FROM {source} WHERE {val1} > 1 AND ({val2} <> 'STRVAL' OR {val1} = {val3}) AND")


"""
EXECUTION TESTS (Covering application of SQL to data)
"""
def test_referencefilter_selected():
    parser = _Parser("SELECT {val1}, {val2},{val3} FROM {source}")
    print(parser._references.references)
    source = {f"val{i}" : f"Value {i}" for i in range(1, 11)}
    expected = {f"val{i}" : f"Value {i}" for i in range(1, 4)}
    assert(parser.filter_fields(source) == expected)

def test_referencefilter_all():
    parser = _Parser("SELECT * FROM {source}")
    source = {f"val{i}" : f"Value {i}" for i in range(1, 11)}
    assert(parser.filter_fields(source) == source)

def test_no_where():
    parser = _Parser("SELECT {val1}, {val2},{val3} FROM {source}")
    data = [{f"val{i}" : val for i in range(1, 11)} for val in range(0, 4)]
    result = [record for record in data if parser.satisfied(record)]
    assert(len(result) == len(data))

def test_simple_where():
    parser = _Parser("SELECT {val1}, {val2},{val3} FROM {source} WHERE {val1} > 1")
    data = [{f"val{i}" : val for i in range(1, 11)} for val in range(0, 4)]
    result = [record for record in data if parser.satisfied(record)]
    assert(len(result) == 2)
    for record in result:
        assert(record["val1"] > 1)

def test_where_and():
    parser = _Parser("SELECT {val1}, {val2},{val3} FROM {source} WHERE {val1} > 1 and {val2} = 2")
    data = [{f"val{i}" : val for i in range(1, 11)} for val in range(0, 4)]
    result = [record for record in data if parser.satisfied(record)]
    assert(len(result) == 1)
    for record in result:
        assert(record["val1"] > 1)
        assert(record["val2"] == 2)

def test_where_not():
    parser = _Parser("SELECT {val1}, {val2},{val3} FROM {source} WHERE NOT {val1} > 1")
    data = [{f"val{i}" : val for i in range(1, 11)} for val in range(0, 4)]
    result = [record for record in data if parser.satisfied(record)]
    assert(len(result) == 2)
    for record in result:
        assert(record["val1"] < 2)

def test_where_or():
    parser = _Parser("SELECT {val1}, {val2},{val3} FROM {source} WHERE {val1} > 2 or {val2} = 1")
    data = [{f"val{i}" : val for i in range(1, 11)} for val in range(0, 4)]
    result = [record for record in data if parser.satisfied(record)]
    assert(len(result) == 2)
    for record in result:
        assert(record["val1"] > 2 or record["val2"] == 1)

def test_where_bracketedand():
    parser = _Parser("SELECT {val1}, {val2},{val3} FROM {source} WHERE ({val1} > 2 and {val2} = 3) or ({val2} = 1 and {val3} = 1)" )
    data = [{f"val{i}" : val for i in range(1, 11)} for val in range(0, 4)]
    result = [record for record in data if parser.satisfied(record)]
    assert(len(result) == 2)
    for record in result:
        assert((record["val1"] > 2 and record["val2"] == 3) or (record["val2"] == 1 and record["val3"] == 1))

def test_where_bracketedor():
    parser = _Parser("SELECT {val1}, {val2},{val3} FROM {source} WHERE ({val1} > 1 or {val2} = 1) and ({val2} = 1 or {val3} = 2)" )
    data = [{f"val{i}" : val for i in range(1, 11)} for val in range(0, 4)]
    result = [record for record in data if parser.satisfied(record)]
    assert(len(result) == 2)
    for record in result:
        assert((record["val1"] > 1 or record["val2"] == 1) and (record["val2"] == 1 or record["val3"] == 2))

def test_where_reference():
    parser = _Parser("SELECT {val1}, {val2},{val3} FROM {source} WHERE {val1} = {val2}" )
    data = [{f"val{i}" : val for i in range(1, 11)} for val in range(0, 4)]
    result = [record for record in data if parser.satisfied(record)]
    assert(len(result) == 4)
    for record in result:
        assert(record["val1"] == record["val2"])

def test_where_string():
    parser = _Parser("SELECT {val1}, {val2},{val3} FROM {source} WHERE {val1} = 'Val1'" )
    data = [{f"val{i}" : f"Val{val}" for i in range(1, 11)} for val in range(0, 4)]
    result = [record for record in data if parser.satisfied(record)]
    assert(len(result) == 1)
    for record in result:
        assert(record["val1"] == "Val1")

def test_invalid_reference_left():
    parser = _Parser("SELECT {val1}, {val2},{val3} FROM {source} WHERE {val4} = {val1}" )
    data = [{f"val{i}" : i for i in range(1, 3)} for val in range(0, 4)]
    with pytest.raises(UnrecognisedReferenceError):
        result = [record for record in data if parser.satisfied(record)]

def test_invalid_reference_right():
    parser = _Parser("SELECT {val1}, {val2},{val3} FROM {source} WHERE {val1} = {val4}" )
    data = [{f"val{i}" : i for i in range(1, 4)} for val in range(0, 4)]
    with pytest.raises(UnrecognisedReferenceError):
        result = [record for record in data if parser.satisfied(record)]

def test_gt():
    parser = _Parser("SELECT {val1}, {val2},{val3} FROM {source} WHERE {val1} > 1" )
    data = [{f"val{i}" : val for i in range(1, 4)} for val in range(0, 4)]
    result = [record for record in data if parser.satisfied(record)]
    assert(len(result) == 2)
    for record in result:
        assert(record["val1"] > 1)

def test_gte():
    parser = _Parser("SELECT {val1}, {val2},{val3} FROM {source} WHERE {val1} >= 1" )
    data = [{f"val{i}" : val for i in range(1, 4)} for val in range(0, 4)]
    result = [record for record in data if parser.satisfied(record)]
    assert(len(result) == 3)
    for record in result:
        assert(record["val1"] >= 1)

def test_lt():
    parser = _Parser("SELECT {val1}, {val2},{val3} FROM {source} WHERE {val1} < 2" )
    data = [{f"val{i}" : val for i in range(1, 4)} for val in range(0, 4)]
    result = [record for record in data if parser.satisfied(record)]
    assert(len(result) == 2)
    for record in result:
        assert(record["val1"] < 2)

def test_lte():
    parser = _Parser("SELECT {val1}, {val2},{val3} FROM {source} WHERE {val1} <= 2" )
    data = [{f"val{i}" : val for i in range(1, 4)} for val in range(0, 4)]
    result = [record for record in data if parser.satisfied(record)]
    assert(len(result) == 3)
    for record in result:
        assert(record["val1"] <= 2)

def test_ne():
    parser = _Parser("SELECT {val1}, {val2},{val3} FROM {source} WHERE {val1} <> 2" )
    data = [{f"val{i}" : val for i in range(1, 4)} for val in range(0, 4)]
    result = [record for record in data if parser.satisfied(record)]
    assert(len(result) == 3)
    for record in result:
        assert(record["val1"] != 2)
