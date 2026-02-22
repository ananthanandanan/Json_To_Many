#!/usr/bin/env bash
# Release helper: bumps version, commits, and tags.
#
# Usage:
#   ./scripts/release.sh          # defaults to patch
#   ./scripts/release.sh patch
#   ./scripts/release.sh minor
#   ./scripts/release.sh major
#
# After this script, run:
#   git push && git push origin v<version>
#   gh release create v<version> --title "v<version>" --generate-notes
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

uv version --bump "$BUMP"
VERSION=$(uv version --short)

git add pyproject.toml uv.lock
git commit -m "chore: bump version to $VERSION"
git tag "v$VERSION"

echo ""
echo "Version bumped to $VERSION and tagged v$VERSION."
echo ""
echo "Next steps:"
echo "  git push && git push origin v$VERSION"
echo "  gh release create v$VERSION --title \"v$VERSION\" --generate-notes"
echo "  uv build && uv publish"
