"""Tests for validators module"""

import pytest

from promptpy.validators import (
    CharacterValidator,
    ChoiceValidator,
    DateValidator,
    FloatValidator,
    IntegerValidator,
    Length,
    Unique,
    ValidationError,
)


class TestCharacterValidator:
    def test_valid_characters_returns_none(self):
        v = CharacterValidator(valid="abcde")
        assert v("abc") is None

    def test_invalid_characters_raises_error(self):
        v = CharacterValidator(valid="abcde")
        with pytest.raises(ValidationError):
            v("xyz")

    def test_excluded_characters_returns_none(self):
        v = CharacterValidator(invalid="abcde")
        assert v("xyz") is None

    def test_excluded_characters_raises_error(self):
        v = CharacterValidator(invalid="abcde")
        with pytest.raises(ValidationError):
            v("abc")

    def test_case_insensitive_validation_returns_none(self):
        v = CharacterValidator(valid="abcde")
        assert v("ABC") is None

    def test_case_sensitive_validation_returns_none(self):
        v = CharacterValidator(valid="abcde", case_sensitive=True)
        assert v("abc") is None

    def test_case_sensitive_validation_raises_error(self):
        v = CharacterValidator(valid="abcde", case_sensitive=True)
        with pytest.raises(ValidationError):
            v("ABC")


class TestIntegerValidator:
    def test_validator_returns_none(self):
        v = IntegerValidator()
        assert v("3") is None

    def test_empty_string_returns_none(self):
        v = IntegerValidator()
        assert v("") is None

    def test_accept_empty_false_raises_error(self):
        v = IntegerValidator(accept_empty=False)
        with pytest.raises(ValidationError):
            v("")

    def test_accept_empty_false_returns_none(self):
        v = IntegerValidator(accept_empty=False)
        assert v("3") is None

    def test_min_returns_none(self):
        v = IntegerValidator(min=3)
        assert v("3") is None

    def test_min_raises_error(self):
        v = IntegerValidator(min=3)
        with pytest.raises(ValidationError):
            v("2")

    def test_max_returns_none(self):
        v = IntegerValidator(max=3)
        assert v("3") is None

    def test_max_raises_error(self):
        v = IntegerValidator(max=3)
        with pytest.raises(ValidationError):
            v("4")

    def test_non_number_raises_error(self):
        v = IntegerValidator()
        with pytest.raises(ValidationError):
            v("abc")

    def test_float_raises_error(self):
        v = IntegerValidator()
        with pytest.raises(ValidationError):
            v("1.3")


class TestFloatValidator:
    def test_validator_returns_none(self):
        v = FloatValidator()
        assert v("3.2") is None

    def test_empty_string_returns_none(self):
        v = FloatValidator()
        assert v("") is None

    def test_accept_empty_false_raises_error(self):
        v = FloatValidator(accept_empty=False)
        with pytest.raises(ValidationError):
            v("")

    def test_accept_empty_false_returns_none(self):
        v = FloatValidator(accept_empty=False)
        assert v("3.2") is None

    def test_min_returns_none(self):
        v = FloatValidator(min=3.0)
        assert v("3") is None

    def test_min_raises_error(self):
        v = FloatValidator(min=3.0)
        with pytest.raises(ValidationError):
            v("2.9")

    def test_max_returns_none(self):
        v = FloatValidator(max=3.0)
        assert v("3") is None

    def test_max_raises_error(self):
        v = FloatValidator(max=3)
        with pytest.raises(ValidationError):
            v("4.7")

    def test_non_number_raises_error(self):
        v = FloatValidator()
        with pytest.raises(ValidationError):
            v("abc")


class TestLength:
    def test_min_returns_none(self):
        v = Length(min=2)
        assert v("abc") is None

    def test_min_raises_error(self):
        v = Length(min=2)
        with pytest.raises(ValidationError):
            v("a")

    def test_max_returns_none(self):
        v = Length(max=3)
        assert v("abc") is None

    def test_max_raises_error(self):
        v = Length(max=3)
        with pytest.raises(ValidationError):
            v("abcd")

    def test_exact_returns_none(self):
        v = Length(exact=3)
        assert v("abc") is None

    def test_exact_raises_error(self):
        v = Length(exact=3)
        with pytest.raises(ValidationError):
            v("abcd")


class TestUnique:
    def test_unique_returns_none(self):
        v = Unique()
        assert v("abc") is None

    def test_unique_raises_error(self):
        v = Unique()
        with pytest.raises(ValidationError):
            v("abb")

    def test_unique_ignores_case(self):
        v = Unique()
        with pytest.raises(ValidationError):
            v("aBb")

    def test_unique_case_sensitive_returns_none(self):
        v = Unique(case_sensitive=True)
        assert v("aBb") is None

    def test_unique_case_sensitive_raises_error(self):
        v = Unique(case_sensitive=True)
        with pytest.raises(ValidationError):
            v("aBB")


class TestChoiceValidator:
    def test_returns_none(self):
        v = ChoiceValidator(["hello", "goodbye"])
        assert v("hello") is None

    def test_raises_error(self):
        v = ChoiceValidator(["hello", "goodbye"])
        with pytest.raises(ValidationError):
            v("ciao")

    def test_case_insensitive_by_default(self):
        v = ChoiceValidator(["hello", "goodbye"])
        assert v("HELLO") is None

    def test_case_sensitive_returns_none(self):
        v = ChoiceValidator(["hello", "goodbye"], case_sensitive=True)
        assert v("hello") is None

    def test_case_sensitive_raises_error(self):
        v = ChoiceValidator(["hello", "goodbye"], case_sensitive=True)
        with pytest.raises(ValidationError):
            v("HELLO")

    def test_accepts_empty_string_by_default(self):
        v = ChoiceValidator(["hello", "goodbye"])
        assert v("") is None

    def test_accept_empty_raises_error(self):
        v = ChoiceValidator(["hello", "goodbye"], accept_empty=False)
        with pytest.raises(ValidationError):
            v("")


class TestDateValidator:
    def test_returns_none(self):
        v = DateValidator("%d/%m/%Y")
        assert v("10/03/2022") is None

    def test_raises_error(self):
        v = DateValidator("%d/%m/%Y")
        with pytest.raises(ValidationError):
            v("0/0/0")

    def test_accepts_empty_string(self):
        v = DateValidator("%d/%m/%Y")
        assert v("") is None

    def test_empty_string_raises_error(self):
        v = DateValidator("%d/%m/%Y", accept_empty=False)
        with pytest.raises(ValidationError):
            v("")
