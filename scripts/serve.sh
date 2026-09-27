#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
export PYTHONPATH="$ROOT/src"
export HF_HOME="$ROOT/.cache/huggingface"
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export PYTHONDONTWRITEBYTECODE=1
exec "$ROOT/.venv/bin/python" -m uvicorn openjevtest.api:app \
  --host 127.0.0.1 --port "${JEV_PORT:-8765}" --workers 1 --no-access-log
