promptpy
========

**A Python command-line input and validation library.**

**promptpy** prompts for and validates a range of different data types
on the command line. Out of the box it supports limited character sets,
integers, floats, dates, yes/no, choices, lists and single-character commands::

   from promptpy import Prompt
   prompt = Prompt()
   number = prompt.integer("Pick a number", min=1, max=10, default=7)

The prompt is displayed as ``Pick a number (1-10) [7]:`` and the user is
re-prompted with a context-specific error message until a valid integer is
entered, or accepts the default by pressing Enter.

It is easy to add other types of prompt and validation by creating
custom validators.

For more detail see the :doc:`usage` documentation.

Installation
------------

``promptpy`` requires Python 3.12 or later. To install, run::

    (.venv) $ pip install promptpy

or, if you use `uv <https://docs.astral.sh/uv/>`_::

    $ uv add promptpy

.. toctree::
   :maxdepth: 2
   :caption: Contents

   usage
   api
