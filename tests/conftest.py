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
    """

    def __init__(self):
        self._console = Console()
        self._input = []

    def register(self, text):
        self._input = text
        self.g = iter(self._input)

    def input(self, text):
        # Empty input returns "", otherwise the next item in the sequence
        entered = next(self.g) if self._input else ""
        self._console.print(f"{text}{entered}")
        return entered


@pytest.fixture
def mock_console():
    return MockConsole()
