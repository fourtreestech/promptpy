promptpy
========

**A Python command-line input and validation library.**

**promptpy** prompts for and validates a range of different data types
on the command line. Out of the box it supports limited character sets,
integers, floats, dates, yes/no, lists and single-character commands::

   from promptpy import Prompt
   prompt = Prompt()
   choice = prompt.integer("Pick a number", min=1, max=10, default=7)

It is easy to add other types of prompt and validation by creating
custom validators.

For more detail see the :doc:`usage` documentation.

Installation
------------

To install, run::

    (.venv) $ pip install promptpy

.. toctree::
   :maxdepth: 2
   :caption: Contents

   usage
   api
