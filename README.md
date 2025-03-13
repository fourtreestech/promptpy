# promptpy

**A Python command-line input and validation library.**

![version](https://img.shields.io/badge/version-0.1.0-blue)
![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Ffourtreestech%2Fpromptpy%2Fmain%2Fpyproject.toml)
![coverage](https://img.shields.io/badge/coverage-100%25-green)

**promptpy** prompts for and validates a range of different data types
on the command line. Out of the box it supports limited character sets,
integers, floats, dates, yes/no, lists and single-character commands:

    from promptpy import Prompt

    prompt = Prompt()
    choice = prompt.integer("Pick a number", min=1, max=10, default=7)
    # Prompt is displayed as:
    # Pick a number (1-10) [7]:

The user will be reprompted with context-specific error messages
until a valid integer is entered.

It is easy to add other types of prompt and validation by creating
custom validators.

For more detail see the [documentation](https://promptpy.readthedocs.io/).

## Installation

    (.venv) $ pip install promptpy

## Examples

### Options

    from promptpy import Prompt

    prompt = Prompt()
    options = {
        's': 'to solve',
        'p': 'to play',
        'q': 'to quit',
    }
    choice = prompt.options(options, default='s')
    # Prompt is displayed as:
    # Enter S to solve, P to play, Q to quit [S]:

### Yes/No

    from promptpy import Prompt

    prompt = Prompt()
    choice = prompt.yes_no("Again", default="y")
    # Prompt is displayed as:
    # Again (Y/N)? [Y]:

### Date

    import datetime
    from promptpy import Prompt

    prompt = Prompt()
    date = prompt.date('Enter a date (dd/mm/yyyy)', '%d/%m/%Y', default=datetime.date(2024, 1, 1))
    # Prompt is displayed as:
    # Enter a date (dd/mm/yyyy) [01/01/2024]:

See the [Usage](https://promptpy.readthedocs.io/en/latest/usage.html) section
of the documentation for a full list of methods, or the
[prompt](https://promptpy.readthedocs.io/en/latest/prompt.html) module for details
of methods and parameters.
