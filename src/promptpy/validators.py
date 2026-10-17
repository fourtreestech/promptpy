"""Validators for command-line input.

A validator is a callable that takes a string as its single parameter
and raises a :exc:`~promptpy.validators.ValidationError` if the string is invalid
according to its validation rules. It returns ``None`` if the string is valid.

Pass a list of validators to :meth:`promptpy.prompt.Prompt.prompt`. They are run in
order, and the user is re-prompted after the first one that fails. The message of
the :exc:`ValidationError` is shown to the user in red followed by a full stop,
so it should be short and should not end with punctuation.

Any callable will do, so a plain function can be used as a validator:

.. code-block:: python

   from promptpy import Prompt
   from promptpy.validators import ValidationError

   def not_blank(text: str) -> None:
       if not text.strip():
           raise ValidationError("Please enter some text")

   name = Prompt().prompt("Name", validators=[not_blank])

The built-in validators below are classes which are configured when
constructed and then called with the string to validate. Most accept the
empty string by default (``accept_empty=True``), leaving the decision on whether
a value is required to the :class:`~promptpy.prompt.Prompt` method;
pass ``accept_empty=False`` to reject it.
"""

import math
import unicodedata
from collections import Counter
from datetime import datetime
from string import digits
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

    Both ``valid`` and ``invalid`` may be given, in which case both rules
    apply. The empty string is always accepted.

    Args:
        valid: String of the only characters allowed in the text (default=None)
        invalid: String of characters which may not appear in the text (default=None)
        case_sensitive: ``True`` for case-sensitive comparison (default=False)
    """

    def __init__(
        self,
        valid: Optional[str] = None,
        invalid: Optional[str] = None,
        case_sensitive: bool = False,
    ) -> None:
        """Initialize the validator."""
        self.valid = valid
        self.invalid = invalid
        self.case_sensitive = case_sensitive

    def __call__(self, text: str) -> None:
        """Validate a string.

        Validates according to the rules set on the class instance
        and raises a :exc:`ValidationError` if validation fails.

        Args:
            text: string to validate

        Raises:
            ValidationError: if validation fails
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

       Whole numbers written as floats are accepted:

       >>> v('3.0')
       >>> v('1e3')

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

    Args:
        min: The value cannot be lower than this (default=None)
        max: The value cannot be higher than this (default=None)
        accept_empty: Whether the validator should accept the empty string (default=True)
    """

    def __init__(
        self,
        min: Optional[int] = None,
        max: Optional[int] = None,
        accept_empty: bool = True,
    ) -> None:
        """Initialize the validator."""
        self.min = min
        self.max = max
        self.accept_empty = accept_empty

    def __call__(self, text: str) -> None:
        """Validate a string.

        Validates according to the rules set on the class instance
        and raises a :exc:`ValidationError` if validation fails.

        Args:
            text: string to validate

        Raises:
            ValidationError: if validation fails
        """
        # Check for empty string
        if not text:
            if self.accept_empty:
                return None
            else:
                raise ValidationError("Not a number") from None

        # Convert to an int, falling back to a float for input such as '3.0' or '1e3'
        try:
            i = int(text)
        except ValueError:
            try:
                f = float(text)
            except ValueError:
                raise ValidationError("Not a number") from None

            # Is it an int?
            if not f.is_integer():
                raise ValidationError("Not a whole number") from None
            i = int(f)

        # Check min/max
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

       ``nan`` and ``inf`` are not accepted:

       >>> v('nan')
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

    Args:
        min: The value cannot be lower than this (default=None)
        max: The value cannot be higher than this (default=None)
        accept_empty: Whether the validator should accept the empty string (default=True)
    """

    def __init__(
        self,
        min: Optional[float] = None,
        max: Optional[float] = None,
        accept_empty: bool = True,
    ) -> None:
        """Initialize the validator."""
        self.min = min
        self.max = max
        self.accept_empty = accept_empty

    def __call__(self, text: str) -> None:
        """Validate a string.

        Validates according to the rules set on the class instance
        and raises a :exc:`ValidationError` if validation fails.

        Args:
            text: string to validate

        Raises:
            ValidationError: if validation fails
        """
        # Check for empty string
        if not text:
            if self.accept_empty:
                return None
            else:
                raise ValidationError("Not a number") from None

        # Convert to a float
        try:
            f = float(text)
        except ValueError:
            raise ValidationError("Not a number") from None

        # Reject nan and inf
        if not math.isfinite(f):
            raise ValidationError("Not a number") from None

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

    Every character is checked, not just letters.

    Args:
        case_sensitive: If ``False`` (the default) letter case is ignored
            when comparing characters, so that ``aA`` fails validation.
            If ``True``, ``a`` and ``A`` are considered different
            and ``aA`` passes validation.
    """

    def __init__(self, case_sensitive: bool = False) -> None:
        """Initialize the validator."""
        self.case_sensitive = case_sensitive

    def __call__(self, text: str) -> None:
        """Validate a string.

        Validates according to the rules set on the class instance
        and raises a :exc:`ValidationError` if validation fails.

        Args:
            text: string to validate

        Raises:
            ValidationError: if validation fails
        """
        c = Counter(text if self.case_sensitive else [ch.casefold() for ch in text])
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

    A value of ``0`` for any argument means that the check is not applied.
    If ``exact`` is given it is checked first.

    Args:
        min: The string to validate must contain at least this number of characters (default=0)
        max: The string to validate cannot be longer than this number of characters (default=0)
        exact: The string to validate must contain exactly this number of characters (default=0)
    """

    def __init__(self, min: int = 0, max: int = 0, exact: int = 0) -> None:
        """Initialize the validator."""
        self.min = min
        self.max = max
        self.exact = exact

    def __call__(self, text: str) -> None:
        """Validate a string.

        Validates according to the rules set on the class instance
        and raises a :exc:`ValidationError` if validation fails.

        Args:
            text: string to validate

        Raises:
            ValidationError: if validation fails
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

    Args:
        choices: The string to validate must be an item in this list
        case_sensitive: If True, the validation will use a case-sensitive comparison (default=False)
        accept_empty: Whether the validator should accept the empty string (default=True)
    """

    def __init__(
        self,
        choices: list[str],
        case_sensitive: bool = False,
        accept_empty: bool = True,
    ) -> None:
        """Initialize the validator."""
        self.choices = choices
        self.case_sensitive = case_sensitive
        self.accept_empty = accept_empty

    def __call__(self, text: str) -> None:
        """Validate a string.

        Validates according to the rules set on the class instance
        and raises a :exc:`ValidationError` if validation fails.

        Args:
            text: string to validate

        Raises:
            ValidationError: if validation fails
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

    Args:
        format: The format string used to parse the date
        accept_empty: Whether the validator should accept the empty string (default=True)
    """

    def __init__(self, format: str, accept_empty: bool = True) -> None:
        """Initialize the validator."""
        self.format = format
        self.accept_empty = accept_empty

    def __call__(self, text: str) -> None:
        """Validate a string.

        Validates according to the rules set on the class instance
        and raises a :exc:`ValidationError` if validation fails.

        Args:
            text: string to validate

        Raises:
            ValidationError: if validation fails
        """
        # Check for empty string
        if not text:
            if self.accept_empty:
                return None
            else:
                raise ValidationError("Not a valid date") from None

        # Try parsing the text
        try:
            datetime.strptime(text, self.format)
        except ValueError:
            raise ValidationError("Not a valid date") from None


class PasswordRulesValidator:
    """Validates that an input string complies with a set of password complexity rules.

    Set password rules via the constructor, the validator will
    check that the input string complies with the rules.

    Set any combination of the following rules:

    - Minimum length
    - Contains at least one lowercase character
    - Contains at least one uppercase character
    - Contains at least one numerical digit
    - Contains at least one symbol (any Unicode punctuation or symbol character,
      such as ``!``, ``$``, ``£`` or ``€``; whitespace does not count)

    To validate a string pass it as a parameter when calling
    the class instance. If validation fails it will raise a :exc:`ValidationError`.
    If one rule is violated the ValidationError will state which rule is not met;
    if more than one the ValidationError will list the rules that are not met.

    .. doctest::

       >>> from promptpy.validators import PasswordRulesValidator, ValidationError
       >>> v = PasswordRulesValidator(min_length=12)
       >>> v('abcdefghijkl')
       >>> v('xyz')
       Traceback (most recent call last):
           ...
       promptpy.validators.ValidationError: Password must be at least 12 characters

       >>> v = PasswordRulesValidator(lower=True)
       >>> v('Abcdefghijkl')
       >>> v('XYZ')
       Traceback (most recent call last):
           ...
       promptpy.validators.ValidationError: Password does not contain a lowercase letter

       >>> v = PasswordRulesValidator(upper=True)
       >>> v('Abcdefghijkl')
       >>> v('xyz')
       Traceback (most recent call last):
           ...
       promptpy.validators.ValidationError: Password does not contain an uppercase letter

       >>> v = PasswordRulesValidator(digit=True)
       >>> v('Abcdefghijkl1')
       >>> v('xyz')
       Traceback (most recent call last):
           ...
       promptpy.validators.ValidationError: Password does not contain a numerical digit

       >>> v = PasswordRulesValidator(symbol=True)
       >>> v('Abcdefghijkl1$')
       >>> v('xyz')
       Traceback (most recent call last):
           ...
       promptpy.validators.ValidationError: Password does not contain a symbol

       >>> v = PasswordRulesValidator(min_length=8, upper=True, digit=True)
       >>> v('Abcdefghijkl1$')
       >>> v('xyz')
       Traceback (most recent call last):
           ...
       promptpy.validators.ValidationError: Password must be at least 8 characters and contain an uppercase letter and a digit

       >>> v('XYZ')
       Traceback (most recent call last):
           ...
       promptpy.validators.ValidationError: Password must be at least 8 characters and contain a digit

       >>> v('Xyzxyzxyz')
       Traceback (most recent call last):
           ...
       promptpy.validators.ValidationError: Password does not contain a numerical digit

       >>> v = PasswordRulesValidator(min_length=8)
       >>> v('')

       >>> v = PasswordRulesValidator(min_length=8, accept_empty=False)
       >>> v('')
       Traceback (most recent call last):
           ...
       promptpy.validators.ValidationError: Password cannot be empty

    Args:
        min_length: Minimum password length (default=0)
        lower: True if the password must contain at least one lowercase letter (default=False)
        upper: True if the password must contain at least one uppercase letter (default=False)
        digit: True if the password must contain at least one digit (0-9) (default=False)
        symbol: True if the password must contain at least one Unicode punctuation or symbol character (default=False)
        accept_empty: Whether the validator should accept the empty string (default=True)
    """

    def __init__(
        self,
        min_length: int = 0,
        lower: bool = False,
        upper: bool = False,
        digit: bool = False,
        symbol: bool = False,
        accept_empty: bool = True,
    ) -> None:
        """Initialize the validator."""
        self.min_length = min_length
        self.lower = lower
        self.upper = upper
        self.digit = digit
        self.symbol = symbol
        self.accept_empty = accept_empty

    def _rules(
        self, min_length: int, lower: bool, upper: bool, digit: bool, symbol: bool
    ) -> str:
        """Summary of the given rules in user-friendly str format."""
        rules: list[str] = []

        if lower and upper:
            rules.append("an uppercase and a lowercase letter")

        elif lower:
            rules.append("a lowercase letter")

        elif upper:
            rules.append("an uppercase letter")

        if digit:
            rules.append("a digit")

        if symbol:
            rules.append("a symbol")

        if rules:
            combined = ", ".join(rules[:-1])
            combined = f"{combined} and {rules[-1]}" if combined else rules[-1]
        else:
            combined = ""

        if min_length:
            rule_str = f"Password must be at least {min_length} characters"
            if combined:
                rule_str = f"{rule_str} and contain {combined}"

        elif combined:
            rule_str = f"Password must contain {combined}"

        else:
            rule_str = ""

        return rule_str

    def __call__(self, text: str) -> None:
        """Validate a string.

        Validates according to the rules set on the class instance
        and raises a :exc:`ValidationError` if validation fails.

        Args:
            text: string to validate

        Raises:
            ValidationError: if validation fails
        """
        # Check for empty string
        if not text:
            if self.accept_empty:
                return None
            else:
                raise ValidationError("Password cannot be empty")

        errors: list[str] = []
        # Check for length
        too_short = bool(self.min_length) and len(text) < self.min_length
        if too_short:
            errors.append(f"Password must be at least {self.min_length} characters")

        # Check for lower case
        no_lower = self.lower and not any(letter.islower() for letter in text)
        if no_lower:
            errors.append("Password does not contain a lowercase letter")

        # Check for upper case
        no_upper = self.upper and not any(letter.isupper() for letter in text)
        if no_upper:
            errors.append("Password does not contain an uppercase letter")

        # Check for digit
        no_digit = self.digit and not any(letter in digits for letter in text)
        if no_digit:
            errors.append("Password does not contain a numerical digit")

        # Check for symbol
        no_symbol = self.symbol and not any(
            unicodedata.category(letter)[0] in "PS" for letter in text
        )
        if no_symbol:
            errors.append("Password does not contain a symbol")

        # Single error - flag which rule has been violated
        if len(errors) == 1:
            raise ValidationError(errors[0])

        # Multiple errors - list out the rules that were violated
        elif errors:
            raise ValidationError(
                self._rules(
                    self.min_length if too_short else 0,
                    no_lower,
                    no_upper,
                    no_digit,
                    no_symbol,
                )
            )
