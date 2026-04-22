#!/usr/bin/env bash
set -euo pipefail

uv sync --frozen
uv run pytest tests/test_output_schema.py -q
