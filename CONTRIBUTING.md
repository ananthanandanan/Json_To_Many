# Contributing to Json2Many

Thanks for your interest in contributing. Here's what you need to know.

## Setup

```bash
git clone https://github.com/ananthanandanan/Json_To_Many.git
cd Json_To_Many
uv sync --extra cli --dev
uv run pre-commit install
```

## Before you open a PR

```bash
uv run pre-commit run --all-files   # lint + format
uv run pytest                       # all tests must pass
```

## Commit messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

| Prefix | When to use |
|--------|-------------|
| `feat:` | New converter, new option, new CLI flag |
| `fix:` | Bug fix |
| `docs:` | README, GUIDE, docstrings |
| `test:` | Adding or updating tests |
| `refactor:` | Internal restructure, no behaviour change |
| `chore:` | Tooling, deps, CI |

## Adding a new format

1. Create `src/json_to_many/converters/<name>_converter.py` subclassing `BaseConverter`.
2. Register it in the `_CONVERTERS` dict in `src/json_to_many/main.py`.
3. Add the format name to `SUPPORTED_FORMATS` in `src/json_to_many/utils/constants.py`.
4. Expose any format-specific CLI flags in `src/json_to_many/cli/commands/convert.py`.
5. Add a test file at `tests/test_converters/test_<name>_converter.py`.

## Questions

Open a [GitHub Issue](https://github.com/ananthanandanan/Json_To_Many/issues) for bugs, feature
requests, or questions before starting large changes.
