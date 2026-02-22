#!/usr/bin/env bash
# Release helper: bumps version, updates CHANGELOG, commits, and tags.
#
# Usage:
#   ./scripts/release.sh          # defaults to patch
#   ./scripts/release.sh patch
#   ./scripts/release.sh minor
#   ./scripts/release.sh major
#
# After this script, run:
#   git push --follow-tags
#   gh release create v<version> --title "v<version>" --notes-file <(git cliff --latest --strip all)
#   uv build && uv publish

set -euo pipefail

BUMP=${1:-patch}

if [[ ! "$BUMP" =~ ^(patch|minor|major)$ ]]; then
    echo "Error: bump type must be 'patch', 'minor', or 'major' (got '$BUMP')"
    exit 1
fi

# Ensure working tree is clean
if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "Error: working tree has uncommitted changes. Please commit or stash them first."
    exit 1
fi

# Ensure git-cliff is available
if ! command -v git-cliff &> /dev/null; then
    echo "Error: git-cliff is not installed. Install it with: brew install git-cliff"
    exit 1
fi

uv version --bump "$BUMP"
VERSION=$(uv version --short)

# Generate CHANGELOG.md for the new version tag
git cliff --tag "v$VERSION" -o CHANGELOG.md

git add pyproject.toml uv.lock CHANGELOG.md
git commit -m "chore: release v$VERSION"
git tag "v$VERSION"

echo ""
echo "Version bumped to $VERSION and tagged v$VERSION."
echo ""
echo "Next steps:"
echo "  git push --follow-tags"
echo "  gh release create v$VERSION --title \"v$VERSION\" --notes-file <(git cliff --latest --strip all)"
echo "  uv build && uv publish"
