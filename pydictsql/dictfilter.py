from .parser import _Parser
from typing import Union, Generator


class DictFilter:
    """
    Constructs a DictFilter object, taking the SQL which will be applied to filter data
    :param sql: SQL Select statement which is used to filter data
    :raises InvalidTokenError: Raised when tokenising and an invalid value is read
    :raises UnexpectedTokenError: Raised when an unexpected token is encountered parsing the SQL
    """

    def __init__(self, sql: str):
        self._parser = _Parser(sql)

    """
    Applies the SQL provided when instantiated to a list, tuple of records or generator, returning those that match the criteria
    :param kwargs: Single named argument providing the collection to be filtered. The name of the argument must match the FROM reference in the SQL
    :returns: Collection of the same type provided, containing only the records in the source data that match the SQL criteria
    :raises: ValueError if parameters are invalid
    :raises: UnrecognisedReferenceError if a reference is made to a field not in the data
    """

    def filter(self, **kwargs) -> Union[list, tuple]:
        self._validate(**kwargs)
        coll_name = next(iter(kwargs.keys()))
        return (
            tuple(self._filter(kwargs[coll_name]))
            if isinstance(kwargs[coll_name], tuple)
            else self._filter(kwargs[coll_name])
        )

    """
    Applies the SQL provided when instantiated to a list, tuple of records or generator, yielding each machine record in turn
    :param kwargs: Single named argument providing the collection to be filtered. The name of the argument must match the FROM reference in the SQL
    :yields: Each record matching the SQL criteria
    :raises: ValueError if parameters are invalid
    :raises: UnrecognisedReferenceError if a reference is made to a field not in the data
    """

    def filtergen(self, **kwargs):
        self._validate(**kwargs)
        coll_name = next(iter(kwargs.keys()))
        for record in kwargs[coll_name]:
            if self._parser.satisfied(record):
                yield (self._parser.filter_fields(record))

    def _validate(self, is_generator, **kwargs):
        if len(kwargs) != 1:
            raise ValueError(
                "Method takes one named parameter, denoting the data source"
            )
        coll_name = next(iter(kwargs.keys()))
        if coll_name != self._parser.from_ref():
            raise ValueError("Collection name does not match FROM reference in SQL")
        if not (
            isinstance(kwargs[coll_name], list) or isinstance(kwargs[coll_name], tuple or isinstance(kwargs[coll_name], Generator))
        ):
            raise ValueError("Collection to be filtered must be a list, tuple or a generator")

    def _filter(self, source):
        return [
            self._parser.filter_fields(record)
            for record in source
            if self._parser.satisfied(record)
        ]
