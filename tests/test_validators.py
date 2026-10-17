"""Tests for validators module"""

import pytest

from promptpy.validators import (
    CharacterValidator,
    ChoiceValidator,
    DateValidator,
    FloatValidator,
    IntegerValidator,
    Length,
    PasswordRulesValidator,
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


class TestIntegerValidatorPrecision:
    def test_large_int_above_max_raises_error(self):
        v = IntegerValidator(max=12345678901234567890)
        with pytest.raises(ValidationError):
            v("12345678901234567891")

    def test_very_long_int_returns_none(self):
        v = IntegerValidator()
        assert v("9" * 400) is None


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

    @pytest.mark.parametrize("text", ["nan", "NaN", "inf", "-inf", "Infinity"])
    def test_non_finite_raises_error(self, text):
        v = FloatValidator()
        with pytest.raises(ValidationError):
            v(text)

    def test_nan_with_range_raises_error(self):
        v = FloatValidator(min=1.0, max=2.0)
        with pytest.raises(ValidationError):
            v("nan")


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

    @pytest.mark.parametrize("text", ["ﬁ", "ﬃ", "ß", "ﬁf"])
    def test_multichar_casefold_returns_none(self, text):
        v = Unique()
        assert v(text) is None

    def test_casefold_equivalent_chars_raise_error(self):
        v = Unique()
        with pytest.raises(ValidationError):
            v("ßẞ")


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


class TestPasswordRulesValidator:
    def test_no_rules_returns_none(self):
        v = PasswordRulesValidator()
        assert v("") is None

    def test_min_length_returns_none(self):
        v = PasswordRulesValidator(min_length=5)
        assert v("abcde") is None

    def test_min_length_raises_error(self):
        v = PasswordRulesValidator(min_length=5)
        with pytest.raises(ValidationError, match="minimum length"):
            v("abcd")

    def test_lower_returns_none(self):
        v = PasswordRulesValidator(lower=True)
        assert v("ABc") is None

    def test_lower_raises_error(self):
        v = PasswordRulesValidator(lower=True)
        with pytest.raises(ValidationError, match="lowercase letter"):
            v("ABC1")

    def test_upper_returns_none(self):
        v = PasswordRulesValidator(upper=True)
        assert v("abC") is None

    def test_upper_raises_error(self):
        v = PasswordRulesValidator(upper=True)
        with pytest.raises(ValidationError, match="uppercase letter"):
            v("abc1")

    def test_digit_returns_none(self):
        v = PasswordRulesValidator(digit=True)
        assert v("abc1") is None

    def test_digit_raises_error(self):
        v = PasswordRulesValidator(digit=True)
        with pytest.raises(ValidationError, match="numerical digit"):
            v("abc")

    def test_symbol_returns_none(self):
        v = PasswordRulesValidator(symbol=True)
        assert v("abc$") is None

    def test_symbol_raises_error(self):
        v = PasswordRulesValidator(symbol=True)
        with pytest.raises(ValidationError, match="symbol"):
            v("abc1")

    def test_lower_accepts_non_ascii(self):
        v = PasswordRulesValidator(lower=True)
        assert v("ÉCOLEé") is None

    def test_upper_accepts_non_ascii(self):
        v = PasswordRulesValidator(upper=True)
        assert v("écolÉ") is None

    @pytest.mark.parametrize("text", ["abc£", "abc€"])
    def test_symbol_accepts_non_ascii(self, text):
        v = PasswordRulesValidator(symbol=True)
        assert v(text) is None

    def test_symbol_rejects_whitespace(self):
        v = PasswordRulesValidator(symbol=True)
        with pytest.raises(ValidationError, match="symbol"):
            v("abc def")

    def test_all_rules_returns_none(self):
        v = PasswordRulesValidator(
            min_length=8, lower=True, upper=True, digit=True, symbol=True
        )
        assert v("Abcdef1!") is None

    def test_multiple_violations_lists_rules(self):
        v = PasswordRulesValidator(min_length=8, upper=True, digit=True)
        with pytest.raises(ValidationError) as exc_info:
            v("xyz")
        assert str(exc_info.value) == (
            "Password must be at least 8 characters"
            " and contain an uppercase letter and a digit"
        )

    def test_multiple_violations_without_min_length_lists_rules(self):
        v = PasswordRulesValidator(upper=True, digit=True)
        with pytest.raises(ValidationError) as exc_info:
            v("xyz")
        assert str(exc_info.value) == (
            "Password must contain an uppercase letter and a digit"
        )

    def test_rules_summary_for_all_rules(self):
        v = PasswordRulesValidator(
            min_length=8, lower=True, upper=True, digit=True, symbol=True
        )
        assert v._rules() == (
            "Password must be at least 8 characters and contain"
            " an uppercase and a lowercase letter, a digit and a symbol"
        )

    def test_rules_summary_for_lower_only(self):
        v = PasswordRulesValidator(lower=True)
        assert v._rules() == "Password must contain a lowercase letter"

    def test_rules_summary_for_min_length_only(self):
        v = PasswordRulesValidator(min_length=8)
        assert v._rules() == "Password must be at least 8 characters"

    def test_rules_summary_with_no_rules_is_empty(self):
        v = PasswordRulesValidator()
        assert v._rules() == ""
