# Changelog

## [Unreleased]

### Added

- ``Prompt.password()`` prompts for a password, with options to show the input, toggle visibility with ``V`` and confirm the password. Empty passwords are rejected unless ``accept_empty`` is set, and ``validators`` can be supplied

- ``PasswordRulesValidator`` checks minimum length and the presence of lowercase, uppercase, digit and symbol characters (Unicode-aware for letters and symbols)

### Changed

- Docstrings converted from reST field lists to Google style (rendered via ``sphinx.ext.napoleon``)
- Documentation expanded: the usage guide now covers defaults, commands, case transforms, Rich markup and custom validators, and docstrings describe return types, validator edge cases and the ``choice``/``date`` prompt text

### Fixed

- ``Prompt.integer()`` returned a string instead of an int for input such as ``3.0`` or ``1e3``
- ``FloatValidator`` (and so ``Prompt.float()``) accepted ``nan`` and ``inf``
- ``IntegerValidator`` lost precision on integers larger than 2^53, so out-of-range values could pass and very long integers were rejected
- ``Unique`` wrongly rejected input containing characters such as ``ﬁ`` or ``ß`` whose case-folded form is more than one character
- ``Prompt.prompt()`` returned ``default`` without applying ``transform``, unlike typed input and commands
- ``Prompt.string_list()`` returned the default without applying ``transform``
- ``Prompt.integer()`` and ``Prompt.float()`` returned a ``default`` outside ``min``/``max``; they now raise ``ValueError``
- ``Prompt.options()`` interpreted option descriptions as Rich markup, so text in square brackets disappeared and ``[/]`` raised ``MarkupError``
- The custom validator example in the usage guide raised ``ValueError`` for input such as ``7.0`` or an empty string
- Package metadata listed Python 3.9–3.11 classifiers although ``requires-python`` is ``>=3.12``

## [0.2.0] - 2026-05-02

### Changed

- Added default parameters to all ``Prompt`` methods

## [0.1.0] - 2025-03-13

_Initial release._

[0.2.0]: https://github.com/fourtreestech/promptpy/releases/tag/v0.2.0

[0.1.0]: https://github.com/fourtreestech/promptpy/releases/tag/v0.1.0
