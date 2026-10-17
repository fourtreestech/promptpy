import pytest
from rich.console import Console


class MockConsole:
    """Mocks out a Rich console to enable generation of user input.

    Use the :func:`mock_console` fixture to obtain a class
    instance, then register any iterable which will then
    be returned from successive calls to :meth:`~MockConsole.input()`::

        from promptpy import Prompt

        def test_mock_console(mock_console):
            mock_console.register(["no", "yes"])
            prompt = Prompt(mock_console)
            assert prompt.prompt("Finished") == "no"
            assert prompt.prompt("Finished") == "yes"

    The ``password`` flag of each call to :meth:`~MockConsole.input()` is
    recorded in ``hidden``, so tests can check which inputs were hidden.
    """

    def __init__(self):
        self._console = Console()
        self._input = []
        self.hidden = []

    def register(self, text):
        self._input = text
        self.g = iter(self._input)

    def input(self, text, password=False):
        # Empty input returns "", otherwise the next item in the sequence
        entered = next(self.g) if self._input else ""
        self.hidden.append(password)
        self._console.print(f"{text}{entered}")
        return entered

    def print(self, text):
        self._console.print(text)


@pytest.fixture
def mock_console():
    return MockConsole()
