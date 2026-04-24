#!/usr/bin/env bash
# Install sync-skills to ~/.local/bin (idempotent).
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/sync-skills"
DEST="${HOME}/.local/bin/sync-skills"

if [[ ! -x "$SRC" ]]; then
  echo "error: $SRC not found or not executable" >&2
  exit 1
fi

mkdir -p "${HOME}/.local/bin"

if [[ -L "$DEST" ]]; then
  current="$(readlink "$DEST")"
  if [[ "$current" == "$SRC" ]]; then
    echo "ok: $DEST already -> $SRC"
    exit 0
  fi
  echo "replacing existing symlink: $current -> $SRC"
  rm "$DEST"
elif [[ -e "$DEST" ]]; then
  echo "error: $DEST exists and is not a symlink; refusing to overwrite" >&2
  exit 1
fi

ln -s "$SRC" "$DEST"
echo "installed: $DEST -> $SRC"

case ":${PATH}:" in
  *":${HOME}/.local/bin:"*) ;;
  *) echo "warn: ~/.local/bin not on PATH — add to ~/.zshrc: export PATH=\"\$HOME/.local/bin:\$PATH\"" >&2 ;;
esac
