class ImplementationError(BaseException):
    ...


class TestCase:
    label: str
    def __init__(self, label: str) -> None:
        self.label = label

    def __enter__(self) -> None:
        pass

    def __exit__(self, __exc_type, __exc_value, __traceback) -> None:
        if __exc_value is not None:
            raise ImplementationError(f'{self.label}: {__exc_value}')


class RaisesError:
    label: str
    def __init__(self, label: str) -> None:
        self.label = label

    def __enter__(self) -> None:
        pass

    def __exit__(self, __exc_type, __exc_value, __traceback) -> None:
        if __exc_type is None:
            raise ImplementationError(f'{self.label}')


def tressa(condition: bool, error_message: str) -> None:
    """Raises an ImplementationError with the given error_message.
        Replacement for assert statements and AssertionError.
    """
    if condition:
        return
    raise ImplementationError(error_message)
