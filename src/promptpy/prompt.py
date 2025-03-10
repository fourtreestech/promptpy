"""The Prompt class supplies a number of methods which manage command-line input and validation."""

import datetime
from typing import Callable, Literal, Optional, Union, cast

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

CaseTransform = Literal["upper", "lower", "casefold", "none"]


class Prompt:
    """Call methods of this class to prompt for and validate different
    types of data (characters, integers, etc.).

    If you have a Rich Console instance already created, supply
    it to the constructor, otherwise one will be created.

    :param console: Rich console instance, if one has been created (default=None)
    :type console: :class:`~rich.console.Console`
    """

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()

    @staticmethod
    def transform_text(text: str, transform: CaseTransform) -> str:
        """Apply a case transformation.

        The ``transform`` parameter indicates how the text should
        be transformed. It can be one of:

            * 'upper': converted to upper case
            * 'lower': converted to lower case
            * 'casefold`: applies :py:meth:`str.casefold()`
            * 'none': no transformation applied

        :param text: Text to transform
        :type text: str
        :param transform: Transformation to apply
        :type transform: str
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
    ) -> str:
        """Display a command line prompt and return the user input.

        The ``validators`` parameter takes an optional list of validators.
        This is any callable that takes a string as its single parameter
        and raises a :exc:`~clprompt.validators.ValidationError` if the string is invalid
        according to its validation rules.

        If any validation fails the user prompt will be redisplayed,
        preceded by the validation error message.

        ``prompt`` accepts an optional string of case-insensitive single-letter commands.
        If any one of these characters is entered at the prompt
        it will be returned without any further validation being undertaken.

        The ``transform`` parameter indicates how the input string should
        be transformed before returning. It can be one of:

            * 'upper': converted to upper case
            * 'lower': converted to lower case
            * 'casefold`: applies :py:meth:`str.casefold()`
            * 'none': input string is returned as entered

        :param text: Text prompt to display
        :type text: str
        :param validators: Validators to test user input (default=None)
        :type validators: list[Callable[[str], None]]
        :param commands: String of single-letter commands to accept (default='')
        :type commands: str
        :param transform: Transformation to apply to input before returning (default='none')
        :type transform: str
        :returns: Validated user input
        :rtype: str
        """
        valid = False
        err = ""

        while not valid:
            # Display error message if there is one
            if err:
                if "\n" in text:
                    # Multiline display
                    msg = f"\n[bold red]{err}.[/]\n{text}"
                else:
                    # Single line display
                    msg = f"[bold red]{err}.[/] {text}"
            else:
                # No error
                msg = text

            # Get input
            s = self.console.input(f"{msg}: ")

            # Validate input and loop round again if invalid
            valid = True

            # Check for a single-letter command
            if commands and len(s) == 1 and s.casefold() in commands.casefold():
                break

            # Run validators
            if validators:
                for validator in validators:
                    try:
                        validator(s)
                    except ValidationError as e:
                        err = str(e)
                        valid = False
                        break

        return self.transform_text(s, transform)

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

        :param text: Prompt text
        :type text: str
        :param min: Minimum accepted value (default=None)
        :type min: int
        :param max: Maximum accepted value (default=None)
        :type max: int
        :param default: Default value (default=None)
        :type default: int
        :param commands: String of single-letter commands to accept (default='')
        :type commands: str
        :param transform: Transformation to apply to command input before returning (default='upper')
        :type transform: str
        :returns: The integer or command entered at the prompt, or the default value if none was entered
        :rtype: Union[int, str]
        """
        # Number range if one is given
        rng = (
            f" ({min}-{max})"
            if min is not None and max is not None and max > min
            else ""
        )

        # Default if one is given
        if default is not None:
            suffix = f" [{default}]"
            accept_empty = True
        else:
            suffix = ""
            accept_empty = False

        # Get response
        response = self.prompt(
            f"{text}{rng}{suffix}",
            validators=[IntegerValidator(min=min, max=max, accept_empty=accept_empty)],
            commands=commands,
            transform=transform,
        )
        if len(response) == 0:
            return default or 0
        try:
            return int(response)
        except ValueError:
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

        :param text: Prompt text
        :type text: str
        :param min: Minimum accepted value (default=None)
        :type min: float
        :param max: Maximum accepted value (default=None)
        :type max: float
        :param default: Default value (default=None)
        :type default: float
        :param commands: String of single-letter commands to accept (default='')
        :type commands: str
        :param transform: Transformation to apply to command input before returning (default='upper')
        :type transform: str
        :returns: The float or command entered at the prompt, or the default value if none was entered
        :rtype: Union[float, str]
        """
        # Number range if one is given
        rng = (
            f" ({min}-{max})"
            if min is not None and max is not None and max > min
            else ""
        )

        # Default if one is given
        if default is not None:
            suffix = f" [{default}]"
            accept_empty = True
        else:
            suffix = ""
            accept_empty = False

        # Get response
        response = self.prompt(
            f"{text}{rng}{suffix}",
            validators=[FloatValidator(min=min, max=max, accept_empty=accept_empty)],
            commands=commands,
            transform=transform,
        )
        if len(response) == 0:
            return default or 0
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

        Presents user with a text prompt and an options default::

            prompt = Prompt()
            prompt.list("Words to exclude", default=["yes", "no")
            # Prompt is displayed as:
            # Words to exclude [yes, no]:

        Words should be separated by a comma, and will
        be stored without leading or trailing whitespace.

        :param text: Prompt text
        :type text: str
        :param default: Default option (default=None)
        :type default: list[str]
        :param transform: Transformation to apply to input before returning (default='none')
        :type transform: str
        :returns: The words entered at the prompt
        :rtype: list[str]
        """
        suffix = escape(f" [{', '.join(default)}]") if default else ""
        words = self.prompt(f"{text}{suffix}", transform=transform)
        return (
            [word.strip() for word in words.split(",") if len(word.strip())]
            if words
            else default or []
        )

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

        :param text: Prompt text
        :type text: str
        :param default: Default option (default=None)
        :type default: str
        :param transform: Transformation to apply to input before returning (default='upper')
        :type transform: str
        :returns: The letter entered at the prompt
        :rtype: str
        """
        if default:
            suffix = f" [{default.upper()}]"
            min = 0
        else:
            suffix = ""
            min = 1

        choice = self.prompt(
            f"{text} (Y/N)?{suffix}",
            validators=[CharacterValidator(valid="yn"), Length(min=min, max=1)],
            transform=transform,
        )

        return choice or self.transform_text(cast(str, default), transform)

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
        is a description of that option. The function creates
        a prompt to present the options to the user::

            prompt = Prompt()
            options = {
                's': 'to solve',
                'p': 'to play',
                'q': 'to quit',
            }
            choice = prompt.options(options, default='s')
            # Prompt is displayed as:
            # Enter S to solve, P to play, Q to quit [S]:

        If the number of options is greater than or equal to``multi_line``
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

        :param options: Options to display
        :type options: dict[str, str]
        :param default: Default option (default=None)
        :type default: str
        :param transform: Transformation to apply to input before returning (default='upper')
        :type transform: str
        :param multi_line: Lowest number of options to split across multiple lines (default=5)
        :type multi_line: int
        :returns: Selected option, or default option if none is selected
        :rtype: str
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
            [f"[bold]{k.upper()}[/] {v}" for k, v in options.items()]
        )
        letters = "".join(options.keys())
        if default:
            suffix = f" [{default.upper()}]"
            min = 0
        else:
            suffix = ""
            min = 1

        choice = self.prompt(
            f"{prefix}{option_text}{mid}{suffix}",
            [CharacterValidator(valid=letters), Length(min=min, max=1)],
            transform=transform,
        )

        return choice or self.transform_text(cast(str, default), transform)

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
            choice = prompt.choice("Please choose your breakfast", choices, default="ham")
            # Prompt is displayed as:
            # Please choose your breakfast [ham]:

        :param text: Text prompt to display
        :type text: str
        :param choices: List of available choices
        :type choices: list[str]
        :param default: Default option (default=None)
        :type default: str
        :param commands: String of single-letter commands to accept (default='')
        :type commands: str
        :param transform: Transformation to apply to input before returning (default='none')
        :type transform: str
        :returns: Validated user input
        :rtype: str
        """
        if default:
            suffix = escape(f" [{default}]")
            accept_empty = True
        else:
            suffix = ""
            accept_empty = False

        option = self.prompt(
            f"{text}{suffix}",
            [ChoiceValidator(choices, accept_empty=accept_empty)],
            commands=commands,
            transform=transform,
        )
        return option or self.transform_text(cast(str, default), transform)

    def date(
        self,
        text: str,
        format: str,
        default: Optional[datetime.date] = None,
        commands: str = "",
        transform: CaseTransform = "upper",
        accept_empty: bool = False,
    ) -> Union[datetime.date, str]:
        """Prompt for a date

        .. code-block::

           prompt = Prompt()
           date = prompt.date('Enter a date (dd/mm/yyyy)', '%d/%m/%Y', default=datetime.date(2024, 1, 1))
           # Prompt is displayed as:
           # Enter a date (dd/mm/yyyy) [01/01/2024]:

        :param text: Prompt text
        :type text: str
        :param format: Date format as per :meth:`~datetime.datetime.strptime`
        :type format: str
        :param default: Default value (default=None)
        :type default: :class:`datetime.date`
        :param commands: String of single-letter commands to accept (default='')
        :type commands: str
        :param transform: Transformation to apply to command input before returning (default='upper')
        :type transform: str
        :param accept_empty: Accept the empty string as a return value (default=False)
        :type accept_empty: bool
        :returns: The date or command entered at the prompt, or the default value if nothing was entered
        :rtype: datetime.date | str
        """
        if default:
            suffix = escape(f" [{datetime.datetime.strftime(default, format)}]")
            accept_empty = True
        else:
            suffix = ""

        date = self.prompt(
            f"{text}{suffix}",
            [DateValidator(format, accept_empty=accept_empty)],
            commands=commands,
            transform=transform,
        )

        if date:
            try:
                return datetime.datetime.strptime(date, format).date()
            except ValueError:
                return date

        return default or ""
