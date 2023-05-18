from __future__ import annotations


class ImplementationError(BaseException):
    ...

class ImplementationNote(BaseException):
    ...


def tressa(condition: bool, error_message: str) -> None:
    """Raises an ImplementationError with the given error_message if the
        condition is False. Replacement for assert statements and
        AssertionError.
    """
    if condition:
        return
    raise ImplementationError(error_message)


_errors = []

def error(condition: bool, error_message: str) -> None:
    """Adds an ImplementationError with the given error_message to the
        _errors list if the condition is False.
    """
    if condition:
        return
    _errors.append(ImplementationError(error_message))

def get_errors() -> list[ImplementationError]:
    """Returns the list of errors."""
    return [*_errors]

def clear_errors() -> None:
    """Clears the list of errors."""
    _errors.clear()


_notes = []

def note(message: str | ImplementationNote) -> None:
    """Add a message to the _notes list."""
    _notes.append(ImplementationNote(message) if type(message) is str else message)

def eton(condition: bool, message: str) -> None:
    """Raises an ImplementationNote if the condition is False."""
    if condition:
        return
    raise ImplementationNote(message)

def get_notes() -> list[ImplementationNote]:
    """Returns list of notes."""
    return [*_notes]

def clear_notes() -> None:
    """Clears the list of notes."""
    _notes.clear()


def post_test_report() -> None:
    """Report the test results."""
    print('')

    for err in get_errors():
        print(f'error: {err}')

    for nt in get_notes():
        print(f'note: {nt}')

    if len(get_errors()) > 0:
        print(f'Specification test failed with {len(get_errors())} error(s) and {len(get_notes())} note(s).')
    else:
        print(f'Sepcification test passed with {len(get_notes())} note(s).')


class TestCase:
    label: str
    def __init__(self, label: str) -> None:
        self.label = label

    def __enter__(self) -> None:
        pass

    def __exit__(self, __exc_type, __exc_value, __traceback) -> bool | None:
        if __exc_value is not None:
            if __exc_type is ImplementationNote:
                note(__exc_value)
                print('N', end='', sep='', flush=True)
                return True

            print('F', end='', sep='', flush=True)
            error(False, f'{self.label}: {__exc_value}')
            return True

        print('.', end='', sep='', flush=True)


class RaisesError:
    label: str
    exception: None | BaseException

    def __init__(self, label: str) -> None:
        self.label = label
        self.exception = None

    def __enter__(self) -> RaisesError:
        return self

    def __exit__(self, __exc_type, __exc_value, __traceback) -> bool | None:
        if __exc_type is None:
            error(False, f'{self.label}: no error raised')
        self.exception = __exc_value
        return True
