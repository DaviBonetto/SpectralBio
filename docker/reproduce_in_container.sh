#!/usr/bin/env bash
set -euo pipefail

docker build -f docker/Dockerfile -t spectralbio-skill .
docker run --rm spectralbio-skill uv run spectralbio reproduce-all --json --cpu-only --offline
