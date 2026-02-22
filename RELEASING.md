# Releasing a New Version

This document describes the release process for maintainers.

## Prerequisites

- [`uv`](https://docs.astral.sh/uv/) installed
- [`gh`](https://cli.github.com/) (GitHub CLI) installed and authenticated
- PyPI credentials configured for `uv publish`

## Steps

### 1. Ensure the main branch is clean and tests pass

```bash
git checkout main
git pull
uv run pytest
uv run ruff check .
```

### 2. Run the release script

A helper script at `scripts/release.sh` bumps the version in `pyproject.toml`, commits, and tags:

```bash
# Patch release: 0.2.0 → 0.2.1
./scripts/release.sh patch

# Minor release: 0.1.0 → 0.2.0
./scripts/release.sh minor

# Major release: 0.2.0 → 1.0.0
./scripts/release.sh major
```

The script will:
- Validate the bump type
- Check the working tree is clean
- Run `uv version --bump <type>`
- Commit `pyproject.toml` and `uv.lock`
- Create a `v<version>` git tag

### 3. Push the commit and tag

```bash
git push && git push origin v<version>
```

### 4. Create a GitHub Release

Use `--generate-notes` to auto-populate release notes from merged PRs and commits:

```bash
gh release create v<version> --title "v<version>" --generate-notes
```

Or open the GitHub UI: **Releases → Draft a new release → pick the tag**.

### 5. Publish to PyPI

```bash
uv build
uv publish
```

To publish to TestPyPI first (configured in `pyproject.toml`):

```bash
uv publish --index testpypi
```

## Version numbering

This project follows [Semantic Versioning](https://semver.org/):

| Change type | Bump | Example |
|---|---|---|
| Bug fixes, small improvements | `patch` | `0.2.0 → 0.2.1` |
| New features, backward-compatible | `minor` | `0.1.0 → 0.2.0` |
| Breaking API changes | `major` | `0.2.0 → 1.0.0` |
