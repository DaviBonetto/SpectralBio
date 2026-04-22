#!/usr/bin/env bash
set -euo pipefail

uv sync --frozen
uv run spectralbio preflight --json --cpu-only --offline
uv run spectralbio replay --target tp53 --json --cpu-only --offline
