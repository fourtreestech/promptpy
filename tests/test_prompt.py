import datetime

import pytest

from promptpy.prompt import Prompt
from promptpy.validators import CharacterValidator, IntegerValidator, Length


def test_mock_console(mock_console):
    mock_console.register(["no", "yes"])
    prompt = Prompt(mock_console)
    assert prompt.prompt("Finished") == "no"
    assert prompt.prompt("Finished") == "yes"


class TestPrompt:
    def test_prompt_returns_input(self, mock_console, capsys):
        mock_console.register(["abc"])
        prompt = Prompt(mock_console)

        # Prompt should succeed first time
        assert prompt.prompt("Please enter") == "abc"
        assert "Please enter: " in capsys.readouterr().out

    def test_prompt_passes_validation(self, mock_console, capsys):
        mock_console.register(["abc"])
        prompt = Prompt(mock_console)

        # Prompt should succeed first time
        assert (
            prompt.prompt("Please enter", validators=[CharacterValidator(valid="abc")])
            == "abc"
        )
        assert "Please enter: " in capsys.readouterr().out

    def test_prompt_reprompts_if_validation_fails(self, mock_console, capsys):
        mock_console.register(["def", "abc"])
        prompt = Prompt(mock_console)

        # Should fail first time and reprompt
        assert (
            prompt.prompt("Please enter", validators=[CharacterValidator(valid="abc")])
            == "abc"
        )
        assert "Invalid character" in capsys.readouterr().out

    def test_reprompt_on_single_line(self, mock_console, capsys):
        mock_console.register(["def", "abc"])
        prompt = Prompt(mock_console)

        # Should fail first time and reprompt
        assert (
            prompt.prompt("Please enter", validators=[CharacterValidator(valid="abc")])
            == "abc"
        )
        assert "Invalid character(s). " in capsys.readouterr().out

    def test_reprompt_on_mulitiple_lines(self, mock_console, capsys):
        mock_console.register(["def", "abc"])
        prompt = Prompt(mock_console)

        # Should fail first time and reprompt
        assert (
            prompt.prompt(
                "Enter\nA\nB or \nC", validators=[CharacterValidator(valid="abc")]
            )
            == "abc"
        )
        assert "Invalid character(s).\n" in capsys.readouterr().out

    def test_prompt_accepts_command_characters(self, mock_console):
        mock_console.register("d")
        prompt = Prompt(mock_console)

        # Should return the command character, bypassing validation
        assert (
            prompt.prompt(
                "Please enter",
                validators=[CharacterValidator(valid="abc")],
                commands="de",
            )
            == "d"
        )

    def test_transform_none(self, mock_console):
        mock_console.register(["AbCdE"])
        prompt = Prompt(mock_console)
        assert prompt.prompt("Please enter") == "AbCdE"

    def test_transform_upper(self, mock_console):
        mock_console.register(["AbCdE"])
        prompt = Prompt(mock_console)
        assert prompt.prompt("Please enter", transform="upper") == "ABCDE"

    def test_transform_lower(self, mock_console):
        mock_console.register(["AbCdE"])
        prompt = Prompt(mock_console)
        assert prompt.prompt("Please enter", transform="lower") == "abcde"

    def test_transform_casefold(self, mock_console):
        mock_console.register(["AbCdE"])
        prompt = Prompt(mock_console)
        assert prompt.prompt("Please enter", transform="casefold") == "abcde"

    def test_returns_default(self, mock_console):
        prompt = Prompt(mock_console)
        assert prompt.prompt("Please enter", default="x") == "x"

    def test_transforms_default(self, mock_console, capsys):
        prompt = Prompt(mock_console)
        assert prompt.prompt("Please enter", default="AbC", transform="lower") == "abc"
        assert "[abc]" in capsys.readouterr().out

    def test_default_not_validated(self, mock_console):
        prompt = Prompt(mock_console)
        result = prompt.prompt(
            "Please enter", [IntegerValidator(accept_empty=False)], default="x"
        )
        assert result == "x"


class TestOptionsPrompt:
    def test_returns_input(self, mock_console, capsys):
        mock_console.register("s")
        prompt = Prompt(mock_console)

        # Should return the option
        assert prompt.options({"s": "to solve", "p": "to play"}) == "S"
        assert "S to solve" in capsys.readouterr().out

    def test_returns_default(self, mock_console, capsys):
        prompt = Prompt(mock_console)

        # Should return the default option
        assert prompt.options({"s": "to solve", "p": "to play"}, default="s") == "S"
        assert "[S]" in capsys.readouterr().out

    def test_no_default_reprompts(self, mock_console, capsys):
        mock_console.register(["", "S"])
        prompt = Prompt(mock_console)

        # No input - should reprompt
        assert prompt.options({"s": "solve", "p": "play"}) == "S"
        assert "Text too short" in capsys.readouterr().out

    def test_invalid_option(self, mock_console, capsys):
        mock_console.register("zs")
        prompt = Prompt(mock_console)

        # Invalid option - should reprompt
        assert prompt.options({"s": "solve", "p": "play"}) == "S"
        assert "Invalid character(s)" in capsys.readouterr().out

    def test_transforms_case(self, mock_console):
        mock_console.register("S")
        prompt = Prompt(mock_console)

        # Should return the option
        assert (
            prompt.options({"s": "to solve", "p": "to play"}, transform="lower") == "s"
        )

    def test_no_line_break(self, mock_console, capsys):
        mock_console.register("s")
        prompt = Prompt(mock_console)

        # Single line output
        assert prompt.options({"s": "to solve", "p": "to play"}) == "S"
        assert "\nP" not in capsys.readouterr().out

    def test_line_break(self, mock_console, capsys):
        mock_console.register("s")
        prompt = Prompt(mock_console)

        # Single line output
        assert prompt.options({"s": "solve", "p": "play"}, multi_line=2) == "S"
        assert "\nP" in capsys.readouterr().out

    def test_escapes_markup_in_description(self, mock_console, capsys):
        mock_console.register("q")
        prompt = Prompt(mock_console)

        # Square brackets in descriptions are shown literally
        assert prompt.options({"s": "solve", "q": "quit [no save]"}) == "Q"
        assert "Q quit [no save]" in capsys.readouterr().out

    def test_closing_tag_in_description(self, mock_console, capsys):
        mock_console.register("s")
        prompt = Prompt(mock_console)

        # A stray closing tag must not raise MarkupError
        assert prompt.options({"s": "solve [/]", "p": "play"}) == "S"
        assert "solve [/]" in capsys.readouterr().out


class TestYesNoPrompt:
    def test_returns_input(self, mock_console, capsys):
        mock_console.register("y")
        prompt = Prompt(mock_console)

        # Should return 'y'
        assert prompt.yes_no("Again") == "Y"
        assert "Again (Y/N)?" in capsys.readouterr().out

    def test_returns_default(self, mock_console, capsys):
        prompt = Prompt(mock_console)

        # Should return default (y)
        assert prompt.yes_no("Again", default="y") == "Y"
        assert "[Y]" in capsys.readouterr().out

    def test_invalid_input(self, mock_console, capsys):
        mock_console.register("zn")
        prompt = Prompt(mock_console)

        # Invalid input - should reprompt
        assert prompt.yes_no("Again", default="y") == "N"
        assert "Invalid character(s)" in capsys.readouterr().out

    def test_transforms_case(self, mock_console):
        mock_console.register("Y")
        prompt = Prompt(mock_console)

        # Should return 'y'
        assert prompt.yes_no("Again", transform="lower") == "y"


class TestIntegerPrompt:
    def test_returns_input(self, mock_console, capsys):
        mock_console.register("3")
        prompt = Prompt(mock_console)

        # Should succeed first time
        assert prompt.integer("Pick a number") == 3
        assert "Pick a number" in capsys.readouterr().out

    def test_returns_default(self, mock_console, capsys):
        prompt = Prompt(mock_console)

        # Should return default
        assert prompt.integer("Pick a number", default=3) == 3
        assert "[3]" in capsys.readouterr().out

    def test_displays_zero_default(self, mock_console, capsys):
        mock_console.register("3")
        prompt = Prompt(mock_console)

        # Should display default value
        assert prompt.integer("Pick a number", default=0) == 3
        assert "[0]" in capsys.readouterr().out

    def test_returns_zero_default(self, mock_console, capsys):
        prompt = Prompt(mock_console)

        # Should return zero default
        assert prompt.integer("Pick a number", default=0) == 0
        assert "[0]" in capsys.readouterr().out

    def test_non_integer_input_reprompts(self, mock_console, capsys):
        mock_console.register("x3")
        prompt = Prompt(mock_console)

        # Invalid - should reprompt
        assert prompt.integer("Pick a number") == 3
        assert "Not a number" in capsys.readouterr().out

    def test_too_small_reprompts(self, mock_console, capsys):
        mock_console.register("23")
        prompt = Prompt(mock_console)

        # Invalid - should reprompt
        assert prompt.integer("Pick a number", min=3) == 3
        assert "Number should be 3 or greater" in capsys.readouterr().out

    def test_too_large_reprompts(self, mock_console, capsys):
        mock_console.register("43")
        prompt = Prompt(mock_console)

        # Invalid - should reprompt
        assert prompt.integer("Pick a number", max=3) == 3
        assert "Number should be 3 or less" in capsys.readouterr().out

    def test_returns_command(self, mock_console, capsys):
        mock_console.register("q")
        prompt = Prompt(mock_console)

        # Returns command 'q'
        assert prompt.integer("Pick a number", max=3, commands="q") == "Q"

    def test_displays_range(self, mock_console, capsys):
        mock_console.register("3")
        prompt = Prompt(mock_console)

        # Should display valid range
        assert prompt.integer("Pick a number", min=1, max=5) == 3
        assert "(1-5)" in capsys.readouterr().out

    def test_whole_number_float_returns_int(self, mock_console, capsys):
        mock_console.register(["3.0"])
        prompt = Prompt(mock_console)

        # Validator accepts '3.0' - should be returned as an int
        result = prompt.integer("Pick a number")
        assert result == 3
        assert isinstance(result, int)

    def test_exponent_returns_int(self, mock_console, capsys):
        mock_console.register(["1e3"])
        prompt = Prompt(mock_console)

        # Validator accepts '1e3' - should be returned as an int
        result = prompt.integer("Pick a number", max=5000)
        assert result == 1000
        assert isinstance(result, int)

    def test_large_int_returned_exactly(self, mock_console, capsys):
        mock_console.register(["12345678901234567891"])
        prompt = Prompt(mock_console)

        # Large ints should not lose precision
        assert prompt.integer("Pick a number") == 12345678901234567891

    def test_doesnt_display_zero_range(self, mock_console, capsys):
        mock_console.register("3")
        prompt = Prompt(mock_console)

        # Shouldn't display zero range
        assert prompt.integer("Pick a number", min=3, max=3) == 3
        assert "(3-3)" not in capsys.readouterr().out

    @pytest.mark.parametrize("default", [0, 11])
    def test_default_out_of_range_raises_error(self, mock_console, default):
        prompt = Prompt(mock_console)

        # Out-of-range default is a programming error
        with pytest.raises(ValueError):
            prompt.integer("Pick a number", min=1, max=10, default=default)

    def test_default_at_boundary_returned(self, mock_console):
        prompt = Prompt(mock_console)

        assert prompt.integer("Pick a number", min=1, max=10, default=10) == 10


class TestFloatPrompt:
    def test_returns_input(self, mock_console, capsys):
        mock_console.register("3")
        prompt = Prompt(mock_console)

        # Should return 3.0
        assert prompt.float("Pick a number") == 3.0
        assert "Pick a number" in capsys.readouterr().out

    def test_returns_default(self, mock_console, capsys):
        prompt = Prompt(mock_console)

        # Should return default
        assert prompt.float("Pick a number", default=3.0) == 3.0
        assert "[3.0]" in capsys.readouterr().out

    def test_displays_zero_default(self, mock_console, capsys):
        mock_console.register("3")
        prompt = Prompt(mock_console)

        # Should display default
        assert prompt.float("Pick a number", default=0.0) == 3.0
        assert "[0.0]" in capsys.readouterr().out

    def test_returns_zero_default(self, mock_console, capsys):
        prompt = Prompt(mock_console)

        # Should return 0.0
        assert prompt.float("Pick a number", default=0.0) == 0.0
        assert "[0.0]" in capsys.readouterr().out

    def test_non_number_input_reprompts(self, mock_console, capsys):
        mock_console.register("x3")
        prompt = Prompt(mock_console)

        # Should reprompt for valid input
        assert prompt.float("Pick a number") == 3.0
        assert "Not a number" in capsys.readouterr().out

    def test_nan_reprompts(self, mock_console, capsys):
        mock_console.register(["nan", "1.5"])
        prompt = Prompt(mock_console)

        # nan is invalid - should reprompt
        assert prompt.float("Pick a number", min=1, max=2) == 1.5
        assert "Not a number" in capsys.readouterr().out

    def test_too_small_reprompts(self, mock_console, capsys):
        mock_console.register("23")
        prompt = Prompt(mock_console)

        # Should reprompt for valid input
        assert prompt.float("Pick a number", min=3.0) == 3.0
        assert "Number should be 3.0 or greater" in capsys.readouterr().out

    def test_too_large_reprompts(self, mock_console, capsys):
        mock_console.register("43")
        prompt = Prompt(mock_console)

        # Should reprompt for valid input
        assert prompt.float("Pick a number", max=3.0) == 3.0
        assert "Number should be 3.0 or less" in capsys.readouterr().out

    def test_display_range(self, mock_console, capsys):
        mock_console.register("3")
        prompt = Prompt(mock_console)

        # Should display range
        assert prompt.float("Pick a number", min=1.0, max=5.0) == 3.0
        assert "(1.0-5.0)" in capsys.readouterr().out

    def test_doesnt_display_zero_range(self, mock_console, capsys):
        mock_console.register("3")
        prompt = Prompt(mock_console)

        # Shouldn't display non-range
        assert prompt.float("Pick a number", min=3.0, max=3.0) == 3.0
        assert "(3.0-3.0)" not in capsys.readouterr().out

    def test_returns_command(self, mock_console, capsys):
        mock_console.register("q")
        prompt = Prompt(mock_console)

        # Returns command 'q'
        assert prompt.float("Pick a number", max=3.0, commands="q") == "Q"

    @pytest.mark.parametrize("default", [0.5, 2.5])
    def test_default_out_of_range_raises_error(self, mock_console, default):
        prompt = Prompt(mock_console)

        # Out-of-range default is a programming error
        with pytest.raises(ValueError):
            prompt.float("Pick a number", min=1.0, max=2.0, default=default)

    def test_default_at_boundary_returned(self, mock_console):
        prompt = Prompt(mock_console)

        assert prompt.float("Pick a number", min=1.0, max=2.0, default=1.0) == 1.0


class TestStringListPrompt:
    def test_returns_entered_text(self, mock_console, capsys):
        mock_console.register(["word 1"])
        prompt = Prompt(mock_console)

        # Should return text
        assert prompt.string_list("Enter words") == ["word 1"]
        assert "Enter words: " in capsys.readouterr().out

    def test_returns_list_of_text(self, mock_console, capsys):
        mock_console.register(["word 1, word 2"])
        prompt = Prompt(mock_console)

        # Should return list of strings
        assert prompt.string_list("Enter words") == ["word 1", "word 2"]
        assert "Enter words: " in capsys.readouterr().out

    def test_returns_default(self, mock_console, capsys):
        prompt = Prompt(mock_console)

        # Should return default
        assert prompt.string_list("Enter words", default=["word 1", "word 2"]) == [
            "word 1",
            "word 2",
        ]
        assert "[word 1, word 2]" in capsys.readouterr().out

    def test_transforms_default(self, mock_console, capsys):
        prompt = Prompt(mock_console)

        # Default should be transformed like typed input
        assert prompt.string_list(
            "Enter words", default=["Yes", "No"], transform="lower"
        ) == ["yes", "no"]
        assert "[yes, no]" in capsys.readouterr().out

    def test_returns_empty_list(self, mock_console, capsys):
        prompt = Prompt(mock_console)

        # Should return empty list
        assert prompt.string_list("Enter words") == []
        assert "Enter words: " in capsys.readouterr().out

    def test_removes_empty_strings(self, mock_console, capsys):
        mock_console.register(["one, two, , four"])
        prompt = Prompt(mock_console)

        # Should remove the empty string
        assert prompt.string_list("Enter words") == ["one", "two", "four"]

    def test_transforms_case(self, mock_console):
        mock_console.register(["word 1, word 2"])
        prompt = Prompt(mock_console)

        # Should return list of strings
        assert prompt.string_list("Enter words", transform="upper") == [
            "WORD 1",
            "WORD 2",
        ]


class TestChoicePrompt:
    def test_returns_entered_text(self, mock_console, capsys):
        mock_console.register(["ham"])
        prompt = Prompt(mock_console)

        # Should return entered text
        assert prompt.choice("Choose your breakfast", ["ham", "spam", "eggs"]) == "ham"
        assert "Choose your breakfast: " in capsys.readouterr().out

    def test_returns_default(self, mock_console, capsys):
        prompt = Prompt(mock_console)

        # Should return default
        assert (
            prompt.choice(
                "Choose your breakfast", ["ham", "spam", "eggs"], default="ham"
            )
            == "ham"
        )
        assert "[ham]" in capsys.readouterr().out

    def test_rejects_empty_string_if_no_default(self, mock_console, capsys):
        mock_console.register(["", "ham"])
        prompt = Prompt(mock_console)

        # Should reprompt for second input
        assert prompt.choice("Choose your breakfast", ["ham", "spam", "eggs"]) == "ham"
        assert "not a valid option" in capsys.readouterr().out

    def test_returns_command(self, mock_console, capsys):
        mock_console.register("q")
        prompt = Prompt(mock_console)

        # Should return command
        assert (
            prompt.choice(
                "Choose your breakfast, or Q to quit",
                ["ham", "spam", "eggs"],
                commands="q",
            )
            == "q"
        )
        assert "Q to quit" in capsys.readouterr().out

    def test_transforms_case(self, mock_console):
        mock_console.register(["ham"])
        prompt = Prompt(mock_console)

        # Should return entered text in upper case
        assert (
            prompt.choice(
                "Choose your breakfast", ["ham", "spam", "eggs"], transform="upper"
            )
            == "HAM"
        )


class TestDatePrompt:
    def test_returns_entered_date(self, mock_console, capsys):
        mock_console.register(["20/03/2024"])
        prompt = Prompt(mock_console)

        # Should return date as entered
        assert prompt.date("Enter a date", "%d/%m/%Y") == datetime.date(2024, 3, 20)
        assert "Enter a date: " in capsys.readouterr().out

    def test_returns_default(self, mock_console, capsys):
        prompt = Prompt(mock_console)

        # Should return default
        assert prompt.date(
            "Enter a date", "%d/%m/%Y", default=datetime.date(2024, 3, 20)
        ) == datetime.date(2024, 3, 20)
        assert "[20/03/2024]" in capsys.readouterr().out

    def test_rejects_empty_string_if_no_default(self, mock_console, capsys):
        mock_console.register(["", "20/03/2024"])
        prompt = Prompt(mock_console)

        # Should reprompt for second input
        assert prompt.date("Enter a date", "%d/%m/%Y") == datetime.date(2024, 3, 20)
        assert "Not a valid date" in capsys.readouterr().out

    def test_returns_empty_string(self, mock_console, capsys):
        prompt = Prompt(mock_console)

        # Should accept empty string
        assert prompt.date("Enter a date", "%d/%m/%Y", accept_empty=True) == ""

    def test_returns_command(self, mock_console, capsys):
        mock_console.register("q")
        prompt = Prompt(mock_console)

        # Should return command
        assert (
            prompt.date(
                "Enter a date, or Q to quit",
                "%d/%m/%Y",
                commands="q",
            )
            == "Q"
        )
        assert "Q to quit" in capsys.readouterr().out

    def test_transforms_case(self, mock_console):
        mock_console.register("Q")
        prompt = Prompt(mock_console)

        # Should return command
        assert (
            prompt.date(
                "Enter a date, or Q to quit",
                "%d/%m/%Y",
                commands="q",
                transform="lower",
            )
            == "q"
        )

    def test_rejects_invalid_date_format(self, mock_console, capsys):
        mock_console.register(["20/03/2024", "20/03/24"])
        prompt = Prompt(mock_console)

        assert prompt.date("Enter a date", "%d/%m/%y") == datetime.date(2024, 3, 20)
        assert "Not a valid date" in capsys.readouterr().out


class TestPasswordPrompt:
    def test_returns_password(self, mock_console):
        mock_console.register(["password1"])
        prompt = Prompt(mock_console)

        assert prompt.password() == "password1"
        assert mock_console.hidden == [True]

    def test_show_input(self, mock_console):
        mock_console.register(["password1"])
        prompt = Prompt(mock_console)

        assert prompt.password(show_input=True) == "password1"
        assert mock_console.hidden == [False]

    def test_confirms_password(self, mock_console):
        mock_console.register(["password1", "password1"])
        prompt = Prompt(mock_console)

        assert prompt.password(confirm=True) == "password1"
        assert mock_console.hidden == [True, True]

    def test_rejects_unmatched_passwords(self, mock_console, capsys):
        mock_console.register(["password1", "password2", "password1", "password1"])
        prompt = Prompt(mock_console)

        assert prompt.password(confirm=True) == "password1"
        out = capsys.readouterr().out
        assert "Passwords don't match" in out
        assert "[red]" not in out

    def test_toggle_visibility(self, mock_console):
        mock_console.register(["v", "password1"])
        prompt = Prompt(mock_console)

        assert prompt.password(toggle_visibility=True) == "password1"
        assert mock_console.hidden == [True, False]

    def test_toggle_visibility_twice(self, mock_console):
        mock_console.register(["v", "v", "password1"])
        prompt = Prompt(mock_console)

        assert prompt.password(toggle_visibility=True) == "password1"
        assert mock_console.hidden == [True, False, True]

    def test_confirm_uses_toggled_visibility(self, mock_console):
        mock_console.register(["v", "password1", "password1"])
        prompt = Prompt(mock_console)

        assert prompt.password(toggle_visibility=True, confirm=True) == "password1"
        assert mock_console.hidden == [True, False, False]

    def test_toggle_on_confirm(self, mock_console, capsys):
        mock_console.register(["password1", "v", "password1"])
        prompt = Prompt(mock_console)

        assert prompt.password(toggle_visibility=True, confirm=True) == "password1"
        assert mock_console.hidden == [True, True, False]
        assert "Passwords don't match" not in capsys.readouterr().out

    def test_confirm_shows_toggle_hint(self, mock_console, capsys):
        mock_console.register(["password1", "password1"])
        prompt = Prompt(mock_console)

        prompt.password(toggle_visibility=True, confirm=True)
        assert "Confirm password (V to toggle visibility)" in capsys.readouterr().out

    def test_rejects_empty_password(self, mock_console, capsys):
        mock_console.register(["", "password1"])
        prompt = Prompt(mock_console)

        assert prompt.password() == "password1"
        assert "Password cannot be empty" in capsys.readouterr().out
        assert mock_console.hidden == [True, True]

    def test_accept_empty(self, mock_console):
        mock_console.register([""])
        prompt = Prompt(mock_console)

        assert prompt.password(accept_empty=True) == ""

    def test_validators(self, mock_console, capsys):
        mock_console.register(["short", "password1"])
        prompt = Prompt(mock_console)

        assert prompt.password(validators=[Length(min=8)]) == "password1"
        assert "Text too short" in capsys.readouterr().out

    def test_toggle_bypasses_validators(self, mock_console):
        mock_console.register(["V", "password1"])
        prompt = Prompt(mock_console)

        assert (
            prompt.password(toggle_visibility=True, validators=[Length(min=8)])
            == "password1"
        )
        assert mock_console.hidden == [True, False]

    def test_confirm_not_validated(self, mock_console):
        mock_console.register(["password1", "password1"])
        prompt = Prompt(mock_console)

        assert prompt.password(confirm=True, validators=[Length(min=8)]) == "password1"
        assert mock_console.hidden == [True, True]

    def test_v_is_password_without_toggle(self, mock_console):
        mock_console.register(["v"])
        prompt = Prompt(mock_console)

        assert prompt.password() == "v"
        assert mock_console.hidden == [True]
