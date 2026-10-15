Usage
=====

The ``Prompt`` class
--------------------

The simplest way to use ``promptpy`` is to create an
instance of the :class:`~promptpy.prompt.Prompt` class, and use its methods
to get and validate command line input::

    from promptpy import Prompt

    prompt = Prompt()
    number = prompt.integer("Pick a number", min=1, max=10, default=7)

This will display the command line prompt::

    Pick a number (1-10) [7]:

Input is validated and the method re-prompts if necessary, displaying a
context-specific error message, until valid input is entered::

    Pick a number (1-10) [7]: 12
    Number should be 10 or less. Pick a number (1-10) [7]:

Pressing Enter without typing anything accepts the default, so ``number``
above is the ``int`` ``7``.

Methods
-------

:class:`~promptpy.prompt.Prompt` has a method for each common type of data.
Each returns a value of the appropriate type, except where noted
under :ref:`commands <usage-commands>`.

.. list-table::
   :header-rows: 1
   :widths: 25 20 55

   * - Method
     - Returns
     - Prompts for
   * - :meth:`~promptpy.prompt.Prompt.integer`
     - ``int``
     - A whole number, optionally within a ``min``/``max`` range
   * - :meth:`~promptpy.prompt.Prompt.float`
     - ``float``
     - A decimal number, optionally within a ``min``/``max`` range
   * - :meth:`~promptpy.prompt.Prompt.date`
     - :class:`datetime.date`
     - A date in a given :meth:`~datetime.datetime.strptime` format
   * - :meth:`~promptpy.prompt.Prompt.yes_no`
     - ``str``
     - ``'Y'`` or ``'N'``
   * - :meth:`~promptpy.prompt.Prompt.options`
     - ``str``
     - One of a set of single-character options, which are displayed for you
   * - :meth:`~promptpy.prompt.Prompt.choice`
     - ``str``
     - One of a list of words
   * - :meth:`~promptpy.prompt.Prompt.string_list`
     - ``list[str]``
     - A list of words separated by commas
   * - :meth:`~promptpy.prompt.Prompt.prompt`
     - ``str``
     - Anything: the core method, which takes your own validators

For example::

    import datetime

    prompt = Prompt()

    # Enter S to solve, P to play, Q to quit [S]:
    action = prompt.options(
        {"s": "to solve", "p": "to play", "q": "to quit"}, default="s"
    )

    # Again (Y/N)? [Y]:
    again = prompt.yes_no("Again", default="y") == "Y"

    # Please choose your breakfast (ham, eggs, spam) [ham]:
    food = prompt.choice(
        "Please choose your breakfast (ham, eggs, spam)",
        ["ham", "eggs", "spam"],
        default="ham",
    )

    # Words to exclude [yes, no]:
    words = prompt.string_list("Words to exclude", default=["yes", "no"])

    # Enter a date (dd/mm/yyyy) [01/01/2024]:
    when = prompt.date(
        "Enter a date (dd/mm/yyyy)", "%d/%m/%Y", default=datetime.date(2024, 1, 1)
    )

.. note::

   :meth:`~promptpy.prompt.Prompt.choice` and :meth:`~promptpy.prompt.Prompt.date`
   do not add the available choices or the date format to the prompt,
   so include them in the prompt text. :meth:`~promptpy.prompt.Prompt.choice`
   returns what the user typed, so ``HAM`` is returned as ``'HAM'`` unless
   you pass ``transform='lower'``.

Defaults
--------

All of the methods take an optional ``default``. It is shown in square brackets
at the end of the prompt, and is returned if the user presses Enter
without typing anything. Without a default, the typed methods
(:meth:`~promptpy.prompt.Prompt.integer`, :meth:`~promptpy.prompt.Prompt.date`,
etc.) keep prompting until they get valid input.

:meth:`~promptpy.prompt.Prompt.integer` and :meth:`~promptpy.prompt.Prompt.float`
raise :exc:`ValueError` if the default is outside ``min`` and ``max``.

With the core :meth:`~promptpy.prompt.Prompt.prompt` method the default is
not validated, but ``transform`` is applied to it, just as it is to typed
input and commands.

.. _usage-commands:

Commands
--------

Many programs need to accept a special key in place of the main input,
such as ``q`` to quit. Pass these as a string of single letters in
``commands``. A command is matched without regard to case, is not passed to
the validators, and is returned as a string transformed by ``transform``
(upper case by default). The return type of such a call is therefore a union
such as ``int | str``, so check what you got back::

    value = prompt.integer("Pick a number", min=1, max=10, commands="qh")
    if value == "Q":
        sys.exit()
    elif value == "H":
        show_help()
    else:
        play(value)

:meth:`~promptpy.prompt.Prompt.integer`, :meth:`~promptpy.prompt.Prompt.float`,
:meth:`~promptpy.prompt.Prompt.date`, :meth:`~promptpy.prompt.Prompt.choice`
and :meth:`~promptpy.prompt.Prompt.prompt` accept commands.

Case transforms
---------------

The ``transform`` parameter changes the case of what is returned. It can be
``'upper'``, ``'lower'``, ``'casefold'`` or ``'none'``. Each method has a
sensible default: ``'upper'`` for
:meth:`~promptpy.prompt.Prompt.yes_no`,
:meth:`~promptpy.prompt.Prompt.options` and the commands of
:meth:`~promptpy.prompt.Prompt.integer`, :meth:`~promptpy.prompt.Prompt.float` and
:meth:`~promptpy.prompt.Prompt.date`, and ``'none'`` elsewhere.

Prompt text and Rich markup
---------------------------

The prompt text is displayed with `Rich <https://rich.readthedocs.io/en/stable/>`_,
so you can use `Rich markup <https://rich.readthedocs.io/en/stable/markup.html>`_
such as ``[bold]``, and ``": "`` is appended for you. If the text should contain
literal square brackets, escape it::

    from rich.markup import escape

    prompt.string_list(escape("Names [comma separated]"))

If validation fails, the error is shown in bold red, followed by a full stop and
then the prompt again. If the prompt text has more than one line, the error is
shown on a line of its own before the prompt.

Validators
----------

All of the above methods call the :meth:`~promptpy.prompt.Prompt.prompt` method
under the hood. This takes a list of **validators**, which check the text
entered at the command line.

A validator is a callable which takes a string as its sole parameter
and raises a :exc:`~promptpy.validators.ValidationError` if validation fails,
or returns ``None``. Validators are run in order, and the user is re-prompted
after the first one that fails.

``promptpy`` ships with a range of validators, such as
:class:`~promptpy.validators.IntegerValidator` and
:class:`~promptpy.validators.Length` - see :doc:`validators` for the full list. You can
combine them yourself::

    from promptpy.validators import CharacterValidator, Length, Unique

    # A five-letter word with no repeated letters
    word = prompt.prompt(
        "Enter a word",
        validators=[CharacterValidator(valid="abcdefghijklmnopqrstuvwxyz"),
                    Length(exact=5), Unique()],
    )

Custom validators
^^^^^^^^^^^^^^^^^

The simplest custom validator is a function. Use the error message to tell the
user what is wrong, without a final full stop::

    from promptpy.validators import ValidationError

    def not_blank(text: str) -> None:
        if not text.strip():
            raise ValidationError("Please enter some text")

    name = prompt.prompt("Name", validators=[not_blank])

For validators with settings, or to build on a built-in one, write a class.
The following validator and prompt only accept prime numbers::

    from promptpy import Prompt
    from promptpy.validators import IntegerValidator, ValidationError

    class PrimeValidator(IntegerValidator):
        """Validates that a string represents a prime number."""

        def __init__(self):
            # Require a whole number of at least 2; reject empty input
            super().__init__(min=2, accept_empty=False)

        def __call__(self, text: str) -> None:
            """Validate a string.

            Args:
                text: string to validate

            Raises:
                ValidationError: if validation fails
            """
            # Check this is an integer 2 or greater
            super().__call__(text)

            # IntegerValidator accepts input such as '7.0', so convert via float
            n = int(float(text))
            if any(n % i == 0 for i in range(2, int(n**0.5) + 1)):
                raise ValidationError(f"{n} is not a prime number")

    def get_prime() -> int:
        """Prompt for a prime number."""
        prompt = Prompt()
        text = prompt.prompt("Please enter a prime number", validators=[PrimeValidator()])
        return int(float(text))

Note that :meth:`~promptpy.prompt.Prompt.prompt` always returns a string,
so convert the result to the type you need.

Rich
----

``promptpy`` uses the `Rich <https://rich.readthedocs.io/en/stable/>`_ library
to provide pretty command-line output.

If you have a Rich :class:`~rich.console.Console`
instance already in your application you should supply it to the
:class:`~promptpy.prompt.Prompt` constructor, so that prompts share its
settings. Otherwise the constructor will create and use its own instance::

    from rich.console import Console
    from promptpy import Prompt

    console = Console(width=80)
    console.print("[bold]Setup[/]")
    prompt = Prompt(console)
