"""Validators for command-line input.

A validator is a callable that takes a string as its single parameter
and raises a :exc:`~promptpy.validators.ValidationError` if the string is invalid
according to its validation rules.
"""

from collections import Counter
from datetime import datetime
from typing import Optional


class ValidationError(Exception):
    """Raised if input validation fails."""


class CharacterValidator:
    """Validates that all characters are or are not within a predefined list.

    To validate a string pass it as a parameter when calling
    the class instance. If validation fails
    it will raise a :exc:`ValidationError`.

    .. doctest::

       >>> from promptpy.validators import CharacterValidator, ValidationError
       >>> v = CharacterValidator(valid='abcde')
       >>> v('abc')
       >>> v('xyz')
       Traceback (most recent call last):
           ...
       promptpy.validators.ValidationError: Invalid character(s)

       >>> v = CharacterValidator(invalid='abcde')
       >>> v('xyz')
       >>> v('abc')
       Traceback (most recent call last):
           ...
       promptpy.validators.ValidationError: Invalid character(s)

       >>> v = CharacterValidator(valid='abcde', case_sensitive=True)
       >>> v('abc')
       >>> v('ABC')
       Traceback (most recent call last):
           ...
       promptpy.validators.ValidationError: Invalid character(s)

    :param valid: All characters must be contained in this list (default=None)
    :type valid: str
    :param invalid: No character may be contained in this list (default=None)
    :type invalid: str
    :param case_sensitive: ``True`` for case_sensitive comparison (default=False)
    :type case_sensitive: bool
    """

    def __init__(
        self,
        valid: Optional[str] = None,
        invalid: Optional[str] = None,
        case_sensitive=False,
    ) -> None:
        self.valid = valid
        self.invalid = invalid
        self.case_sensitive = case_sensitive

    def __call__(self, text: str) -> None:
        """Validate a string.

        Validates according to the rules set on the class instance
        and raises a :exc:`ValidationError` if validation fails.

        :param text: string to validate
        :type text: str
        :raises: :exc:`ValidationError` if validation fails
        """
        # Check that all letters are permitted
        if self.valid is not None:
            valid = (
                self.valid
                if self.case_sensitive
                else "".join([self.valid.lower(), self.valid.upper()])
            )
            if any(letter not in valid for letter in text):
                raise ValidationError("Invalid character(s)")

        # Check that no letters are invalid
        if self.invalid is not None:
            invalid = (
                self.invalid
                if self.case_sensitive
                else "".join([self.invalid.lower(), self.invalid.upper()])
            )
            if any(letter in invalid for letter in text):
                raise ValidationError("Invalid character(s)")


class IntegerValidator:
    """Validates that an input string is a valid integer.

    To validate a string pass it as a parameter when calling
    the class instance. If validation fails
    it will raise a :exc:`ValidationError`.

    .. doctest::

       >>> from promptpy.validators import IntegerValidator, ValidationError
       >>> v = IntegerValidator()
       >>> v('3')
       >>> v('xyz')
       Traceback (most recent call last):
           ...
       promptpy.validators.ValidationError: Not a number

       >>> v('3.2')
       Traceback (most recent call last):
           ...
       promptpy.validators.ValidationError: Not a whole number

       >>> v = IntegerValidator(min=3)
       >>> v('3')
       >>> v('2')
       Traceback (most recent call last):
           ...
       promptpy.validators.ValidationError: Number should be 3 or greater

       >>> v = IntegerValidator(max=6)
       >>> v('3')
       >>> v('7')
       Traceback (most recent call last):
           ...
       promptpy.validators.ValidationError: Number should be 6 or less

       >>> v = IntegerValidator()
       >>> v('')

       >>> v = IntegerValidator(accept_empty=False)
       >>> v('')
       Traceback (most recent call last):
           ...
       promptpy.validators.ValidationError: Not a number

    :param min: The value cannot be lower than this (default=None)
    :type min: int
    :param max: The value cannot be higher than this (default=None)
    :type max: int
    :param accept_empty: Whether the validator should accept the empty string (default=True)
    :type accept_empty: bool
    """

    def __init__(
        self,
        min: Optional[int] = None,
        max: Optional[int] = None,
        accept_empty=True,
    ) -> None:
        self.min = min
        self.max = max
        self.accept_empty = accept_empty

    def __call__(self, text: str) -> None:
        """Validate a string.

        Validates according to the rules set on the class instance
        and raises a :exc:`ValidationError` if validation fails.

        :param text: string to validate
        :type text: str
        :raises: :exc:`ValidationError` if validation fails
        """
        # Check for empty string
        if not text:
            if self.accept_empty:
                return None
            else:
                raise ValidationError("Not a number")

        # Convert to a float
        try:
            f = float(text)
        except ValueError:
            raise ValidationError("Not a number")

        # Is it an int?
        if not f.is_integer():
            raise ValidationError("Not a whole number")

        # Check min/max
        i = int(f)
        if self.min is not None and i < self.min:
            raise ValidationError(f"Number should be {self.min} or greater")
        if self.max is not None and i > self.max:
            raise ValidationError(f"Number should be {self.max} or less")


class FloatValidator:
    """Validates that an input string is a valid float.

    To validate a string pass it as a parameter when calling
    the class instance. If validation fails
    it will raise a :exc:`ValidationError`.

    .. doctest::

       >>> from promptpy.validators import FloatValidator, ValidationError
       >>> v = FloatValidator()
       >>> v('3')
       >>> v('3.2')
       >>> v('xyz')
       Traceback (most recent call last):
           ...
       promptpy.validators.ValidationError: Not a number

       >>> v = FloatValidator(min=3.0)
       >>> v('3.0')
       >>> v('2.8')
       Traceback (most recent call last):
           ...
       promptpy.validators.ValidationError: Number should be 3.0 or greater

       >>> v = FloatValidator(max=6.0)
       >>> v('3.0')
       >>> v('6.1')
       Traceback (most recent call last):
           ...
       promptpy.validators.ValidationError: Number should be 6.0 or less

       >>> v = FloatValidator()
       >>> v('')

       >>> v = FloatValidator(accept_empty=False)
       >>> v('')
       Traceback (most recent call last):
           ...
       promptpy.validators.ValidationError: Not a number

    :param min: The value cannot be lower than this (default=None)
    :type min: float
    :param max: The value cannot be higher than this (default=None)
    :type max: float
    :param accept_empty: Whether the validator should accept the empty string (default=True)
    :type accept_empty: bool
    """

    def __init__(
        self,
        min: Optional[float] = None,
        max: Optional[float] = None,
        accept_empty=True,
    ) -> None:
        self.min = min
        self.max = max
        self.accept_empty = accept_empty

    def __call__(self, text: str) -> None:
        """Validate a string.

        Validates according to the rules set on the class instance
        and raises a :exc:`ValidationError` if validation fails.

        :param text: string to validate
        :type text: str
        :raises: :exc:`ValidationError` if validation fails
        """
        # Check for empty string
        if not text:
            if self.accept_empty:
                return None
            else:
                raise ValidationError("Not a number")

        # Convert to a float
        try:
            f = float(text)
        except ValueError:
            raise ValidationError("Not a number")

        # Check min/max
        if self.min is not None and f < self.min:
            raise ValidationError(f"Number should be {self.min} or greater")
        if self.max is not None and f > self.max:
            raise ValidationError(f"Number should be {self.max} or less")


class Unique:
    """Validates that the text contains no repeated characters.

    To validate a string pass it as a parameter when calling
    the class instance. If validation fails
    it will raise a :exc:`ValidationError`.

    .. doctest::

       >>> from promptpy.validators import Unique, ValidationError
       >>> v = Unique()
       >>> v('abc')
       >>> v('abb')
       Traceback (most recent call last):
           ...
       promptpy.validators.ValidationError: Repeated letter 'b'

       >>> v('aBb')
       Traceback (most recent call last):
           ...
       promptpy.validators.ValidationError: Repeated letter 'b'

       >>> v = Unique(case_sensitive=True)
       >>> v('aBb')

    :param case_sensitive: If ``False`` (the default) the validator will ignore letter case
                           when comparing letters, so that ``aA`` will fail validation.
                           If ``True`` ``a`` and ``A`` are considered as different letters
                           and ``aA`` will pass validation.
    :type case_sensitive: bool
    """

    def __init__(self, case_sensitive=False) -> None:
        self.case_sensitive = case_sensitive

    def __call__(self, text: str) -> None:
        """Validate a string.

        Validates according to the rules set on the class instance
        and raises a :exc:`ValidationError` if validation fails.

        :param text: string to validate
        :type text: str
        :raises: :exc:`ValidationError` if validation fails
        """
        c = Counter(text if self.case_sensitive else text.casefold())
        if len(c) != len(text):
            letter = c.most_common()[0][0]
            raise ValidationError(f"Repeated letter '{letter}'")


class Length:
    """Validates that an input string is of the correct length.

    To validate a string pass it as a parameter when calling
    the class instance. If validation fails
    it will raise a :exc:`ValidationError`.

    .. doctest::

       >>> from promptpy.validators import Length, ValidationError
       >>> v = Length(min=2)
       >>> v('abc')
       >>> v('a')
       Traceback (most recent call last):
           ...
       promptpy.validators.ValidationError: Text too short

       >>> v = Length(max=3)
       >>> v('xyz')
       >>> v('abcde')
       Traceback (most recent call last):
           ...
       promptpy.validators.ValidationError: Text too long

       >>> v = Length(exact=3)
       >>> v('abc')
       >>> v('abcd')
       Traceback (most recent call last):
           ...
       promptpy.validators.ValidationError: Text must be 3 characters long

    :param min: The string to validate must contain at least this number of characters
    :type min: int
    :param max: The string to validate cannot be longer than this number of characters
    :type max: int
    :param exact: The string to validate must contain exactly this number of characters
    :type exact: int
    """

    def __init__(self, min=0, max=0, exact=0) -> None:
        self.min = min
        self.max = max
        self.exact = exact

    def __call__(self, text: str) -> None:
        """Validate a string.

        Validates according to the rules set on the class instance
        and raises a :exc:`ValidationError` if validation fails.

        :param text: string to validate
        :type text: str
        :raises: :exc:`ValidationError` if validation fails
        """
        # Test exact
        if self.exact > 0 and len(text) != self.exact:
            raise ValidationError(
                f"Text must be {self.exact} character{'s' if self.exact > 1 else ''} long"
            )

        # Test min
        if self.min > 0 and len(text) < self.min:
            raise ValidationError("Text too short")

        # Test max
        if self.max > 0 and len(text) > self.max:
            raise ValidationError("Text too long")


class ChoiceValidator:
    """Validates that an input string is one of a pre-defined list of choices.

    To validate a string pass it as a parameter when calling
    the class instance. If validation fails
    it will raise a :exc:`ValidationError`.

    .. doctest::

       >>> from promptpy.validators import ChoiceValidator, ValidationError
       >>> v = ChoiceValidator(['hello', 'goodbye'])
       >>> v('hello')
       >>> v('HELLO')
       >>> v('')
       >>> v('ciao')
       Traceback (most recent call last):
           ...
       promptpy.validators.ValidationError: That is not a valid option

       >>> v = ChoiceValidator(['hello', 'goodbye'], case_sensitive=True)
       >>> v('hello')
       >>> v('HELLO')
       Traceback (most recent call last):
           ...
       promptpy.validators.ValidationError: That is not a valid option

       >>> v = ChoiceValidator(['hello', 'goodbye'], accept_empty=False)
       >>> v('')
       Traceback (most recent call last):
           ...
       promptpy.validators.ValidationError: That is not a valid option

    :param choices: The string to validate must be an item in this list
    :type choices: list[str]
    :param case_sensitive: If True, the validation will use a case-sensitive comparison (default=False)
    :type case_sensitive: bool
    :param accept_empty: Whether the validator should accept the empty string (default=True)
    :type accept_empty: bool
    """

    def __init__(
        self, choices: list[str], case_sensitive=False, accept_empty=True
    ) -> None:
        self.choices = choices
        self.case_sensitive = case_sensitive
        self.accept_empty = accept_empty

    def __call__(self, text: str) -> None:
        """Validate a string.

        Validates according to the rules set on the class instance
        and raises a :exc:`ValidationError` if validation fails.

        :param text: string to validate
        :type text: str
        :raises: :exc:`ValidationError` if validation fails
        """
        if not text:
            if self.accept_empty:
                return None
            else:
                raise ValidationError("That is not a valid option")

        # Adjust for case-sensitive comparison
        choice = text if self.case_sensitive else text.casefold()
        choices = (
            self.choices
            if self.case_sensitive
            else [s.casefold() for s in self.choices]
        )

        if choice not in choices:
            raise ValidationError("That is not a valid option")


class DateValidator:
    """Validates that an input string is a valid date.

    Pass a ``strptime`` format string in the constructor,
    the validator will check that the input string can
    be converted to a date using :meth:`datetime.datetime.strptime`.

    To validate a string pass it as a parameter when calling
    the class instance. If validation fails
    it will raise a :exc:`ValidationError`.

    .. doctest::

       >>> from promptpy.validators import DateValidator, ValidationError
       >>> v = DateValidator('%d/%m/%Y')
       >>> v('10/03/2022')
       >>> v('xyz')
       Traceback (most recent call last):
           ...
       promptpy.validators.ValidationError: Not a valid date

       >>> v('0/0/0')
       Traceback (most recent call last):
           ...
       promptpy.validators.ValidationError: Not a valid date

       >>> v('')
       >>> v = DateValidator('%d/%m/%Y', accept_empty=False)
       >>> v('')
       Traceback (most recent call last):
           ...
       promptpy.validators.ValidationError: Not a valid date

    :param format: The format string used to parse the date
    :type format: str
    :param accept_empty: Whether the validator should accept the empty string (default=True)
    :type accept_empty: bool
    """

    def __init__(self, format: str, accept_empty=True) -> None:
        self.format = format
        self.accept_empty = accept_empty

    def __call__(self, text: str) -> None:
        """Validate a string.

        Validates according to the rules set on the class instance
        and raises a :exc:`ValidationError` if validation fails.

        :param text: string to validate
        :type text: str
        :raises: :exc:`ValidationError` if validation fails
        """
        # Check for empty string
        if not text:
            if self.accept_empty:
                return None
            else:
                raise ValidationError("Not a valid date")

        # Try parsing the text
        try:
            datetime.strptime(text, self.format)
        except ValueError:
            raise ValidationError("Not a valid date")
