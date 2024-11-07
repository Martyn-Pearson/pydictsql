class InvalidTokenError(Exception):
    """
    Raised when tokenising and an invalid value is read
    """
    def __init__(self, token: str):
        super().__init__(f"Invalid token: {token}")


class UnexpectedTokenError(Exception):
    """
    Raised when parsing and an unexpected token is found
    """
    def __init__(self, found, expected = None):
        super().__init__(
            f"Unexpected token, expected {expected or 'end'}, found {found.ttype if found else 'no token'} with value {found.value if found else 'N/A'}."
        )

class UnrecognisedReferenceError(Exception):
    """
    Raised when executing SQL which includes a reference to a field which is not in the data
    """
    def __init__(self, reference):
        super().__init__(
            f"Unrecognised reference {reference}, not present in data."
        )
