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

It is easy to add other types of prompt and validation by creating
custom validators.

For more detail see the documentation.

## Installation

    (.venv) $ pip install promptpy