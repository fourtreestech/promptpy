# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

promptpy is a small Python (>=3.12) library for command-line input and validation, built on `rich` (the only runtime dependency). Packaging and environments are managed with `uv`; tasks are in the `justfile`.

## Commands

- `just test` — run tests (`uv run pytest`). Pytest config in `pyproject.toml` enables `--doctest-modules` with `testpaths` of `tests/` and `src/`, so `>>>` examples in docstrings run as tests and must pass. A plain run does not measure coverage; use `just cov`.
- Single test: `uv run pytest tests/test_prompt.py::test_name` (or `-k <expr>`).
- `just check` — `ruff check --fix` + `ruff format` + `ty check` (via `uvx`). Ruff lint rules are `F`, `I`, `B`, `C4`, `SIM`, `RUF` and `D` (with `D401`), using the Google pydocstyle convention; `D` is ignored under `tests/` and `docs/`.
- `just cov` — tests with coverage (`--cov=promptpy`, missing-line output), then coverage JSON + badge update (the README advertises 100% coverage; keep it there).
- `just docs` — Sphinx build with `-W --keep-going` (warnings are errors, but all are reported) using the `docs` dependency group; sources in `docs/source/`.
- `uv run tox` — run the test suite across Python 3.14, 3.13 and 3.12, plus a `lowest` env (Python 3.12 with `uv_resolution = "lowest-direct"`) that checks the minimum allowed dependency versions. Configured under `[tool.tox]` in `pyproject.toml` (uses `tox-uv`, editable install, `test` dependency group). The standard envs use the `uv-venv-lock-runner`, so they install the versions pinned in `uv.lock`; `lowest` uses `uv-venv-runner` so that the resolution override applies.
- `just upgrade` — `uv lock --upgrade`, `uv sync`, then `uv run tox` to verify the upgraded dependencies.
- `just bump` — bumps the version via bumpver across `pyproject.toml`, `README.md`, `src/promptpy/__init__.py` and `docs/source/conf.py`; don't edit those by hand.
- `just sync` / `tag` / `publish` are release steps (dev→main ff-merge, tag, PyPI upload); don't run them without being asked.

## Architecture

- `src/promptpy/prompt.py` — the `Prompt` class. `Prompt.prompt()` is the core loop: it reads input via `console.input`, short-circuits on an empty input with a `default`, accepts single-letter `commands` without validation, otherwise runs each validator in order and re-prompts with a red error message on the first `ValidationError`. The typed helpers (`integer`, `float`, `string_list`, `yes_no`, `options`, `choice`, `date`) compose validators and delegate to `prompt()`, adding prompt-text decoration (e.g. range, `[default]`) and converting the returned string to the target type. `password()` also delegates to `prompt()` (with hidden input, an empty-password check, optional `V` visibility toggle via `commands` and optional confirmation) but has no `default`/`transform`.
- `src/promptpy/validators.py` — validators are plain callables `(text: str) -> None` that raise `ValidationError`. Built-ins are `CharacterValidator`, `IntegerValidator`, `FloatValidator`, `Unique`, `Length`, `ChoiceValidator`, `DateValidator` and `PasswordRulesValidator`. Custom validators just need to follow this protocol.
- The `Console` is injectable (`Prompt(console)`), which is how tests supply input.

## Testing

`tests/conftest.py` provides a `mock_console` fixture: call `mock_console.register([...])` with the sequence of inputs to return from successive `input()` calls (no registration yields empty strings), then pass it to `Prompt(mock_console)`. `mock_console.hidden` lists the `password` flag of each `input()` call. Tests use `pytest-randomly` under tox, so don't rely on test order.

## Docs

Sphinx docs (`docs/source/`) are autodoc-driven from the docstrings, which are Google-style (`Args:`, `Returns:`, parsed by `sphinx.ext.napoleon`), so keep new public docstrings in that format. Every public class, method and `__init__` needs a docstring whose first line is a summary ending in punctuation, followed by a blank line (ruff `D` rules). Add user-visible changes to `CHANGELOG.md`.
