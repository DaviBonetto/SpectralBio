#!/usr/bin/env bash
set -euo pipefail

uv sync --frozen
uv run spectralbio replay-audit --json --cpu-only --offline
