"""The :class:`Prompt` class manages command-line input and validation.

:meth:`Prompt.prompt` is the core method. It displays a prompt, reads a line of
input and runs it through a list of validators (see :mod:`promptpy.validators`),
redisplaying the prompt with an error message until the input is valid.

The typed helpers :meth:`~Prompt.integer`, :meth:`~Prompt.float`,
:meth:`~Prompt.string_list`, :meth:`~Prompt.yes_no`, :meth:`~Prompt.options`,
:meth:`~Prompt.choice` and :meth:`~Prompt.date` build on it, supplying the
appropriate validators and converting the result to the right type.

Three concepts are shared by all of the methods:

* **default**: returned if the user just presses Enter, and shown in the prompt
  as ``[default]``.
* **commands**: single letters (e.g. ``q`` to quit) which are accepted without
  being validated as the main input type.
* **transform**: a case transformation applied to the returned text.
"""

import datetime
from typing import Callable, Literal, Optional, Union

from rich.console import Console
from rich.markup import escape

from .validators import (
    CharacterValidator,
    ChoiceValidator,
    DateValidator,
    FloatValidator,
    IntegerValidator,
    Length,
    ValidationError,
)

#: Case transformation to apply to text: ``'upper'``, ``'lower'``, ``'casefold'``
#: (see :meth:`str.casefold`) or ``'none'`` for no change.
CaseTransform = Literal["upper", "lower", "casefold", "none"]


def _check_default_in_range(
    default: Optional[float], min: Optional[float], max: Optional[float]
) -> None:
    """Raise ``ValueError`` if a numeric default is outside ``min``/``max``."""
    if default is None:
        return

    if (min is not None and default < min) or (max is not None and default > max):
        raise ValueError(f"default {default} is outside the range min={min}, max={max}")


class Prompt:
    """Prompt for and validate different types of data.

    Call methods of this class to prompt for integers, floats, dates,
    yes/no answers, choices and so on. Each method re-prompts until the
    input is valid.

    If you have a Rich Console instance already created, supply
    it to the constructor, otherwise one will be created
    (with ``highlight=False``, so that prompt text is not automatically
    colorized).

    .. code-block:: python

       from rich.console import Console
       from promptpy import Prompt

       prompt = Prompt(Console(width=60))
       age = prompt.integer("Age", min=0, max=120)

    Args:
        console: Rich console instance, if one has been created (default=None)
    """

    def __init__(self, console: Optional[Console] = None):
        """Initialize the prompt.

        Args:
            console: Rich console instance, if one has been created (default=None)
        """
        self.console = console or Console(highlight=False)

    @staticmethod
    def transform_text(text: str, transform: CaseTransform) -> str:
        """Apply a case transformation.

        The ``transform`` parameter indicates how the text should
        be transformed. It can be one of:

            * ``'upper'``: converted to upper case
            * ``'lower'``: converted to lower case
            * ``'casefold'``: applies :meth:`str.casefold`
            * ``'none'``: no transformation applied

        Args:
            text: Text to transform
            transform: Transformation to apply

        Returns:
            The transformed text
        """
        if transform == "upper":
            return text.upper()

        if transform == "lower":
            return text.lower()

        if transform == "casefold":
            return text.casefold()

        return text

    def prompt(
        self,
        text: str,
        validators: Optional[list[Callable[[str], None]]] = None,
        commands: str = "",
        transform: CaseTransform = "none",
        default: str = "",
        password: bool = False,
    ) -> str:
        """Display a command line prompt and return the user input.

        .. code-block:: python

           prompt = Prompt()
           name = prompt.prompt("Name", validators=[Length(min=2)], default="Bob")
           # Prompt is displayed as:
           # Name [Bob]:

        A colon and space are appended to ``text`` automatically.
        ``text`` is interpreted as `Rich markup
        <https://rich.readthedocs.io/en/stable/markup.html>`_, so literal square
        brackets must be escaped with :func:`rich.markup.escape`.

        The ``validators`` parameter takes an optional list of validators.
        This is any callable that takes a string as its single parameter
        and raises a :exc:`~promptpy.validators.ValidationError` if the string is invalid
        according to its validation rules. Validators are run in order and
        checking stops at the first failure. With no validators any input,
        including an empty string, is accepted.

        If any validation fails the user prompt will be redisplayed,
        preceded by the validation error message in bold red and followed by a full stop
        (so error messages should not end with one). If ``text`` contains a newline
        the message is shown on its own line above the prompt.

        ``prompt`` accepts an optional string of case-insensitive single-letter commands.
        If any one of these characters is entered at the prompt
        it will be returned (after ``transform`` is applied) without any validators being run.

        The ``transform`` parameter indicates how the input string should
        be transformed before returning. It can be one of:

            * ``'upper'``: converted to upper case
            * ``'lower'``: converted to lower case
            * ``'casefold'``: applies :meth:`str.casefold`
            * ``'none'``: input string is returned as entered

        If ``default`` is provided it is displayed in square brackets after the
        prompt text. If the user input is empty, ``default`` is returned
        (and displayed) after ``transform`` is applied, but without being validated.

        If `password`` is True user input will be hidden.

        Args:
            text: Text prompt to display
            validators: Validators to test user input (default=None)
            commands: String of single-letter commands to accept (default='')
            transform: Transformation to apply to input before returning (default='none')
            default: Value to return if no user input is supplied (default='')
            password: Hide user input (default=False)

        Returns:
            Validated user input, a command, or the default value
        """
        valid = False
        err = ""
        user_input = ""

        default = self.transform_text(default, transform)
        prompt_text = " ".join([text, escape(f"[{default}]")]) if default else text

        while not valid:
            # Display error message if there is one
            if err:
                if "\n" in text:
                    # Multiline display
                    msg = f"\n[bold red]{err}.[/]\n{prompt_text}"
                else:
                    # Single line display
                    msg = f"[bold red]{err}.[/] {prompt_text}"
            else:
                # No error
                msg = prompt_text

            # Get input
            user_input = self.console.input(f"{msg}: ", password=password)

            # Return default value
            if default and not user_input:
                return default

            # Validate input and loop round again if invalid
            valid = True

            # Check for a single-letter command
            if (
                commands
                and len(user_input) == 1
                and user_input.casefold() in commands.casefold()
            ):
                break

            # Run validators
            if validators:
                for validator in validators:
                    try:
                        validator(user_input)
                    except ValidationError as e:
                        err = str(e)
                        valid = False
                        break

        return self.transform_text(user_input, transform)

    def integer(
        self,
        text: str,
        min: Optional[int] = None,
        max: Optional[int] = None,
        default: Optional[int] = None,
        commands: str = "",
        transform: CaseTransform = "upper",
    ) -> Union[int, str]:
        """Prompt for an integer.

        .. code-block::

           prompt = Prompt()
           prompt.integer('Pick a number', min=1, max=10, default=7)
           # Prompt is displayed as:
           # Pick a number (1-10) [7]:

        The range is only displayed if both ``min`` and ``max`` are given
        and ``max`` is greater than ``min``. Whole-number input such as
        ``3.0`` or ``1e3`` is accepted and returned as an ``int``.
        An empty input re-prompts unless a ``default`` is given.

        If ``commands`` is given, any of those single letters is accepted and
        returned as a string (transformed by ``transform``, upper case by
        default), so check the type of the result:

        .. code-block:: python

           value = prompt.integer('Pick a number', commands='q')
           if value == 'Q':
               ...  # user chose to quit

        Args:
            text: Prompt text
            min: Minimum accepted value (default=None)
            max: Maximum accepted value (default=None)
            default: Default value (default=None)
            commands: String of single-letter commands to accept (default='')
            transform: Transformation to apply to command input before returning (default='upper')

        Returns:
            The integer or command entered at the prompt, or the default value if none was entered

        Raises:
            ValueError: if ``default`` is outside ``min``/``max``
        """
        _check_default_in_range(default, min, max)

        # Number range if one is given
        rng = (
            f" ({min}-{max})"
            if min is not None and max is not None and max > min
            else ""
        )

        # Get response
        response = self.prompt(
            f"{text}{rng}",
            validators=[IntegerValidator(min=min, max=max, accept_empty=False)],
            commands=commands,
            transform=transform,
            default="" if default is None else str(default),
        )

        try:
            return int(response)
        except ValueError:
            pass

        # Whole-number floats such as '3.0' or '1E3' pass IntegerValidator
        try:
            return int(float(response))
        except ValueError:
            # Command
            return response

    def float(
        self,
        text: str,
        min: Optional[float] = None,
        max: Optional[float] = None,
        default: Optional[float] = None,
        commands: str = "",
        transform: CaseTransform = "upper",
    ) -> Union[float, str]:
        """Prompt for a float.

        .. code-block::

           prompt = Prompt()
           prompt.float('Pick a number', min=1.2, max=3.5, default=2.0)
           # Prompt is displayed as:
           # Pick a number (1.2-3.5) [2.0]:

        The range is only displayed if both ``min`` and ``max`` are given
        and ``max`` is greater than ``min``. ``nan`` and ``inf`` are rejected.
        An empty input re-prompts unless a ``default`` is given.

        If ``commands`` is given, any of those single letters is accepted and
        returned as a string (transformed by ``transform``, upper case by
        default), so check the type of the result.

        Args:
            text: Prompt text
            min: Minimum accepted value (default=None)
            max: Maximum accepted value (default=None)
            default: Default value (default=None)
            commands: String of single-letter commands to accept (default='')
            transform: Transformation to apply to command input before returning (default='upper')

        Returns:
            The float or command entered at the prompt, or the default value if none was entered

        Raises:
            ValueError: if ``default`` is outside ``min``/``max``
        """
        _check_default_in_range(default, min, max)

        # Number range if one is given
        rng = (
            f" ({min}-{max})"
            if min is not None and max is not None and max > min
            else ""
        )

        # Get response
        response = self.prompt(
            f"{text}{rng}",
            validators=[FloatValidator(min=min, max=max, accept_empty=False)],
            commands=commands,
            transform=transform,
            default="" if default is None else str(default),
        )

        try:
            return float(response)
        except ValueError:
            return response

    def string_list(
        self,
        text: str,
        default: Optional[list[str]] = None,
        transform: CaseTransform = "none",
    ) -> list[str]:
        """Prompt for a list of strings.

        Presents user with a text prompt and an optional default::

            prompt = Prompt()
            prompt.string_list("Words to exclude", default=["yes", "no"])
            # Prompt is displayed as:
            # Words to exclude [yes, no]:

        Words should be separated by a comma, and will
        be stored without leading or trailing whitespace. Empty items are
        dropped, so entering nothing (with no default) returns an empty list.

        Args:
            text: Prompt text
            default: Default words (default=None)
            transform: Transformation to apply to input before returning (default='none')

        Returns:
            The words entered at the prompt
        """
        words = self.prompt(
            text,
            transform=transform,
            default="" if default is None else ", ".join(default),
        )
        return [word.strip() for word in words.split(",") if len(word.strip())]

    def yes_no(
        self,
        text: str,
        default: Optional[str] = None,
        transform: CaseTransform = "upper",
    ) -> str:
        """Prompt for a yes/no response.

        Presents user with a y/n option and an optional default::

            prompt = Prompt()
            choice = prompt.yes_no("Again", default="y")
            # Prompt is displayed as:
            # Again (Y/N)? [Y]:

        Input is case-insensitive. With the default ``transform`` the
        result is ``'Y'`` or ``'N'``.

        Args:
            text: Prompt text
            default: Default option, ``'y'`` or ``'n'`` (default=None)
            transform: Transformation to apply to input before returning (default='upper')

        Returns:
            The letter entered at the prompt, or the default if none was entered
        """
        return self.prompt(
            f"{text} (Y/N)?",
            validators=[CharacterValidator(valid="yn"), Length(min=1, max=1)],
            transform=transform,
            default="" if default is None else default,
        )

    def options(
        self,
        options: dict[str, str],
        default: Optional[str] = None,
        transform: CaseTransform = "upper",
        multi_line: int = 5,
    ) -> str:
        """Prompt for one of a list of command options.

        Options are provided as a ``dict`` where the key is the
        character to enter to select the option and the value
        is a description of that option. Keys must be single characters
        and are displayed in upper case; input is case-insensitive.
        The function creates a prompt to present the options to the user::

            prompt = Prompt()
            options = {
                's': 'to solve',
                'p': 'to play',
                'q': 'to quit',
            }
            choice = prompt.options(options, default='s')
            # Prompt is displayed as:
            # Enter S to solve, P to play, Q to quit [S]:

        If the number of options is greater than or equal to ``multi_line``
        the options will be split across multiple lines::

            prompt = Prompt()
            options = {
                's': 'to solve',
                'p': 'to play',
                'q': 'to quit',
            }
            choice = prompt.options(options, default='s', multi_line=2)
            # Prompt is displayed as:
            # S to solve
            # P to play
            # Q to quit
            # Enter choice [S]:

        Args:
            options: Options to display, mapping the key to enter to its description
            default: Key of the default option (default=None)
            transform: Transformation to apply to input before returning (default='upper')
            multi_line: Lowest number of options to split across multiple lines (default=5)

        Returns:
            Key of the selected option, or of the default option if none is selected
        """
        if len(options) >= multi_line:
            prefix = ""
            sep = "\n"
            mid = "\nEnter choice"
        else:
            prefix = "Enter "
            sep = ", "
            mid = ""

        option_text = sep.join(
            [f"[bold]{escape(k.upper())}[/] {escape(v)}" for k, v in options.items()]
        )
        letters = "".join(options.keys())

        return self.prompt(
            f"{prefix}{option_text}{mid}",
            [CharacterValidator(valid=letters), Length(min=1, max=1)],
            transform=transform,
            default="" if default is None else default,
        )

    def choice(
        self,
        text: str,
        choices: list[str],
        default: Optional[str] = None,
        commands: str = "",
        transform: CaseTransform = "none",
    ) -> str:
        """Prompt for one of a list of predefined choices.

        The choices are provided as a list of strings::

            prompt = Prompt()
            choices = ["ham", "eggs", "spam"]
            choice = prompt.choice(
                "Please choose your breakfast (ham, eggs, spam)", choices, default="ham"
            )
            # Prompt is displayed as:
            # Please choose your breakfast (ham, eggs, spam) [ham]:

        The available choices are not displayed automatically, so list them in
        ``text``. Matching is case-insensitive, and the input is returned as
        typed (``'HAM'`` is returned as ``'HAM'``) unless a ``transform`` such as
        ``'lower'`` is given.

        Args:
            text: Text prompt to display
            choices: List of available choices
            default: Default option (default=None)
            commands: String of single-letter commands to accept (default='')
            transform: Transformation to apply to input before returning (default='none')

        Returns:
            The choice or command entered at the prompt, or the default if none was entered
        """
        return self.prompt(
            f"{text}",
            [ChoiceValidator(choices, accept_empty=False)],
            commands=commands,
            transform=transform,
            default="" if default is None else default,
        )

    def date(
        self,
        text: str,
        format: str,
        default: Optional[datetime.date] = None,
        commands: str = "",
        transform: CaseTransform = "upper",
        accept_empty: bool = False,
    ) -> Union[datetime.date, str]:
        """Prompt for a date.

        .. code-block::

           prompt = Prompt()
           date = prompt.date('Enter a date (dd/mm/yyyy)', '%d/%m/%Y', default=datetime.date(2024, 1, 1))
           # Prompt is displayed as:
           # Enter a date (dd/mm/yyyy) [01/01/2024]:

        The expected format is not displayed automatically, so describe it in
        ``text``. The default is shown formatted with ``format``.

        Normally an empty input re-prompts. If ``accept_empty`` is true an empty
        input is accepted and returned as the empty string ``''`` rather than a
        date, as are any commands, so check the type of the result.

        Args:
            text: Prompt text
            format: Date format as per :meth:`~datetime.datetime.strptime`
            default: Default value (default=None)
            commands: String of single-letter commands to accept (default='')
            transform: Transformation to apply to command input before returning (default='upper')
            accept_empty: Accept the empty string as a return value (default=False)

        Returns:
            The date or command entered at the prompt, the default value if nothing was entered,
            or ``''`` if nothing was entered and ``accept_empty`` is true
        """
        date = self.prompt(
            f"{text}",
            [DateValidator(format, accept_empty=accept_empty)],
            commands=commands,
            transform=transform,
            default="" if default is None else datetime.date.strftime(default, format),
        )

        try:
            return datetime.datetime.strptime(date, format).date()
        except ValueError:
            return date

    def password(self, show_input=False, toggle_visibility=False, confirm=False) -> str:
        """Prompt for a password.

        .. code-block::

           prompt = Prompt()
           date = prompt.password()
           # Prompt is displayed as:
           # Enter password:

        If ``show_input`` is False (the default), the password will not show on screen
        as it is typed.

        If ``toggle_visibility`` is True, the user will have the option to toggle whether
        input is shown by entering 'v' at the prompt.

        If ``confirm`` is True, the user will be prompted to enter the password for
        a second time. If the two passwords don't match an error will show and the
        user will be returned to the first password entry.

        Args:
            show_input: Show user input as it is typed (default=False)
            toggle_visibility: The user can switch input visibility on and off (default=False)
            confirm: The user should be prompted to enter the password a second time (default=False)

        Returns:
            The password entered by the user.
        """
        while True:
            # Get password
            text: str = (
                "Enter password ([bold]V[/] to toggle visibility)"
                if toggle_visibility
                else "Enter password"
            )
            pw = self.prompt(text, password=not show_input)

            # Toggle visibility
            if pw.lower() == "v":
                show_input = not show_input

            # Enter password for a second time
            elif confirm:
                pw2 = self.prompt("Confirm password", password=not show_input)
                if pw2 == pw:
                    break
                else:
                    self.console.print(escape("[red]Passwords don't match![/]"))
            else:
                break

        return pw
