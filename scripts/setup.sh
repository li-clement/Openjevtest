#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
if [ "$(uname -s)" != Darwin ] || [ "$(uname -m)" != arm64 ]; then
  echo 'This backend requires macOS on Apple Silicon.' >&2
  exit 1
fi
command -v uv >/dev/null 2>&1 || { echo 'Install uv first: https://docs.astral.sh/uv/getting-started/installation/' >&2; exit 1; }
export UV_CACHE_DIR="$ROOT/.cache/uv"
export UV_HTTP_RETRIES=0
export UV_HTTP_TIMEOUT=60
uv venv --python 3.11 "$ROOT/.venv"
uv pip install --python "$ROOT/.venv/bin/python" --link-mode copy -r "$ROOT/requirements-macos.lock"
echo 'Ready. Next: .venv/bin/python scripts/download_model.py'
