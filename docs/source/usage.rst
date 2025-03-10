Usage
=====

The ``Prompt`` class
--------------------

The simplest way to use ``promptpy`` is to create an
instance of the :class:`~promptpy.prompt.Prompt` class, and use the methods
to get and validate command line input::

    from promptpy import Prompt

    prompt = Prompt()
    prompt.integer("Pick a number", min=1, max=10, default=7)

This will display the command line prompt::

    Pick a number (1-10) [7]: 

Input will be validated and the method will reprompt if necessary,
displaying context-specific error messages
until a valid integer is entered.

Methods
-------

:class:`~promptpy.prompt.Prompt` ships with a variety of methods to prompt for
and validate different types of data:

* :meth:`~promptpy.prompt.Prompt.date` prompt for a date
* :meth:`~promptpy.prompt.Prompt.float` prompt for a floating point decimal number
* :meth:`~promptpy.prompt.Prompt.integer` prompt for an integer
* :meth:`~promptpy.prompt.Prompt.list` prompt for a list of strings, separated by commas
* :meth:`~promptpy.prompt.Prompt.options` prompt for one of a set of single-character options
* :meth:`~promptpy.prompt.Prompt.yes_no` prompt for `yes` or `no`

Validators
----------

All the above methods call the :meth:`~promptpy.prompt.Prompt.prompt` method under the hood.
This method takes a list of **Validators** which validate the text
entered at the command line.

A Validator is a callable which takes a string as its sole parameter
and raises a :exc:`~promptpy.validators.ValidationError` if validation fails,
or returns ``None``.

``promptpy`` ships with a range of validators covering integers, floating
point numbers, etc. - see :doc:`validators` for more detail.

You can easily extend prompt functionality by creating your own
validators. For example, the following creates a validator
and prompt that will only accept prime numbers::

    from promptpy import Prompt
    from promptpy.validators import IntegerValidator, ValidationError

    class PrimeValidator(IntegerValidator):
        """Validates that a string represents a prime number."""

        def __init__(self):
            super().__init__(min=2)

        def __call__(self, text: str) -> None:
            """Validate a string.

            Validates that the string represents a prime number
            and raises a :exc:`ValidationError` if it doesn't.

            :param text: string to validate
            :type text: str
            :raises: :exc:`ValidationError` if validation fails
            """
            # Check this is an integer 2 or greater
            super().__call__(text)

            # Check this is a prime number
            n = int(text)
            for i in range(2, int(n ** 0.5) + 1):
                if n % i == 0:
                    raise ValidationError("{} is not a prime number".format(n))

    def get_prime():
        """Prompt for a prime number"""
        validator = PrimeValidator()
        prompt = Prompt()
        prime = prompt.prompt("Please enter a prime number", validators=[validator])
        print(f"You entered {prime}.")

Rich
----

``promptpy`` uses the `Rich <https://rich.readthedocs.io/en/stable/>`_ library
to provide pretty command-line output.

If you have a Rich :class:`~rich.console.Console`
instance already in your application you should supply it to the 
:class:`~promptpy.prompt.Prompt` constructor. Otherwise the constructor will
create and use its own instance.