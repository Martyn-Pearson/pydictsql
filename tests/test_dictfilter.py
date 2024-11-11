import pytest
import pydictsql


def test_missing_collection():
    filter = pydictsql.DictFilter("SELECT * FROM {collection}")
    with pytest.raises(ValueError):
        filter.filter()


def test_extra_kwargs():
    filter = pydictsql.DictFilter("SELECT * FROM {collection}")
    with pytest.raises(ValueError):
        filter.filter(collection=[], collection2=[])


def test_incorrect_collection():
    filter = pydictsql.DictFilter("SELECT * FROM {collection}")
    with pytest.raises(ValueError):
        filter.filter(collection2=[])


def test_invalid_collections():
    filter = pydictsql.DictFilter("SELECT * FROM {collection}")
    with pytest.raises(ValueError):
        filter.filter(collection=set())

    with pytest.raises(ValueError):
        filter.filter(collection={})

    with pytest.raises(ValueError):
        filter.filter(collection=7)


def test_invalid_collections_gen():
    filter = pydictsql.DictFilter("SELECT * FROM {collection}")
    with pytest.raises(ValueError):
        for result in filter.filtergen(collection=set()):
            pass

    with pytest.raises(ValueError):
        for result in filter.filtergen(collection={}):
            pass

    with pytest.raises(ValueError):
        for result in filter.filtergen(collection=7):
            pass


NAMES = [
    "Adam",
    "Bob",
    "Charles",
    "David",
    "Edward",
    "Frank",
    "Geoff",
    "Hugh",
    "Ian",
    "John",
]
CITIES = [
    "London",
    "London",
    "Birmingham",
    "London",
    "Cardiff",
    "Glasgow",
    "Cardiff",
    "London",
    "Birmingham",
    "Birmingham",
]
SALES = [100, 400, 350, 290, 180, 320, 500, 380, 350, 460]

SOURCE_DATA_LIST = [
    {"name": name, "city": city, "sales": sales}
    for name, city, sales in zip(NAMES, CITIES, SALES)
]


def test_filter_list():
    filter = pydictsql.DictFilter(
        "SELECT {name}, {city} FROM {sales_data} WHERE {sales} > 250"
    )
    result = filter.filter(sales_data=SOURCE_DATA_LIST)
    assert len(result) == 8


def source_gen():
    for name, city, sales in zip(NAMES, CITIES, SALES):
        yield {"name": name, "city": city, "sales": sales}


def test_filter_gen():
    filter = pydictsql.DictFilter(
        "SELECT {name}, {sales} FROM {sales_data} WHERE {sales} > 250"
    )
    records = 0
    names = set()
    for record in filter.filtergen(sales_data=source_gen()):
        assert record["sales"] > 250
        names.add(record["name"])
        records += 1

    assert records == 8
    for expected in [
        "Bob",
        "Charles",
        "David",
        "Frank",
        "Geoff",
        "Hugh",
        "Ian",
        "John",
    ]:
        assert expected in names
