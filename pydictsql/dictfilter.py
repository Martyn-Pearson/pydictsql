from .parser import _Parser
from typing import Union

class DictFilter:
    """
    Constructs a DictFilter object, taking the SQL which will be applied to filter data
    :param sql: SQL Select statement which is used to filter data
    :raises InvalidTokenException: Raised when tokenising and an invalid value is read
    :raises UnexpectedTokenException: Raised when an unexpected token is encountered parsing the SQL
    """
    def __init__(self, sql: str):
        self._parser = _Parser(sql)

    """
    Applies the SQL provided when instantiated to a list or tuple of records, returning those that match the criteria
    :param kwargs: Single named argument providing the collection to be filtered. The name of the argument must match the FROM reference in the SQL
    :returns: Collection of the same type provided, containing only the records in the source data that match the SQL criteria
    :raises: ValueError if parameters are invalid
    :raises: UnrecognisedReferenceException if a reference is made to a field not in the data
    """
    def filter(self, **kwargs) -> Union[list, tuple]:
        if len(kwargs) != 1:
            raise ValueError("Method takes one named parameter, denoting the data source")
        coll_name = next(iter(kwargs.keys()))
        if coll_name != self._parser.fromref:
            raise ValueError("Collection name does not match FROM reference in SQL")
        source = kwargs[coll_name]
        if not(isinstance(source, list) or isinstance(source, tuple)):
            raise ValueError("Collection to be filtered must be a list or tuple")

        return self._filter(source) if isinstance(source, list) else tuple(self._filter(source))
    

    def _filter(self, source):
        return [self._parser.references.filter_fields(record) for record in source if self._parser.where_clause.satisfied(record)]
