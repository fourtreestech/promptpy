# Changelog

## [Unreleased]

### Fixed

- ``Prompt.integer()`` returned a string instead of an int for input such as ``3.0`` or ``1e3``
- ``FloatValidator`` (and so ``Prompt.float()``) accepted ``nan`` and ``inf``
- ``IntegerValidator`` lost precision on integers larger than 2^53, so out-of-range values could pass and very long integers were rejected
- ``Unique`` wrongly rejected input containing characters such as ``ﬁ`` or ``ß`` whose case-folded form is more than one character
- ``Prompt.string_list()`` returned the default without applying ``transform``
- ``Prompt.integer()`` and ``Prompt.float()`` returned a ``default`` outside ``min``/``max``; they now raise ``ValueError``
- ``Prompt.options()`` interpreted option descriptions as Rich markup, so text in square brackets disappeared and ``[/]`` raised ``MarkupError``
- Package metadata listed Python 3.9–3.11 classifiers although ``requires-python`` is ``>=3.12``

## [0.2.0] - 2026-05-02

### Changed

- Added default parameters to all ``Prompt`` methods

## [0.1.0] - 2025-03-13

_Initial release._

[0.2.0]: https://github.com/fourtreestech/promptpy/releases/tag/v0.2.0

[0.1.0]: https://github.com/fourtreestech/promptpy/releases/tag/v0.1.0
