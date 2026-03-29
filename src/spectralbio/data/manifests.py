"""Helpers for manifest generation."""

from __future__ import annotations

import collections
from pathlib import Path
from typing import Any

from spectralbio.utils.hashing import sha256_file


def label_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counter = collections.Counter(int(row["label"]) for row in rows)
    return {"pathogenic": counter.get(1, 0), "benign": counter.get(0, 0)}


def build_dataset_manifest(name: str, role: str, data_path: Path, rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "name": name,
        "role": role,
        "path": str(data_path),
        "count": len(rows),
        "labels": label_counts(rows),
        "sha256": sha256_file(data_path),
    }
