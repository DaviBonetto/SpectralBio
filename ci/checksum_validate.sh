#!/usr/bin/env bash
set -euo pipefail

uv sync --frozen
uv run spectralbio replay-audit --json --cpu-only --offline > /dev/null
uv run spectralbio verify --target tp53 --json --cpu-only --offline
uv run spectralbio verify --target brca2 --json --cpu-only --offline
uv run spectralbio verify --target tsc2 --json --cpu-only --offline
uv run spectralbio verify --target crebbp --json --cpu-only --offline
