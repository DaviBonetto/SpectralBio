"""Simple config loader for the canonical commands."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from spectralbio.constants import (
    BRCA1_TRANSFER_CONFIG_PATH,
    BRCA2_REPLAY_CONFIG_PATH,
    CREBBP_REPLAY_CONFIG_PATH,
    TP53_CONFIG_PATH,
    TSC2_REPLAY_CONFIG_PATH,
)


def load_yaml(path: Path) -> dict[str, Any]:
    config: dict[str, Any] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition(":")
        if not _:
            raise ValueError(f"Invalid config line in {path}: {raw_line!r}")
        config[key.strip()] = value.strip()
    return config


def load_tp53_config() -> dict[str, Any]:
    return load_yaml(TP53_CONFIG_PATH)


def load_brca1_transfer_config() -> dict[str, Any]:
    return load_yaml(BRCA1_TRANSFER_CONFIG_PATH)


def load_brca2_replay_config() -> dict[str, Any]:
    return load_yaml(BRCA2_REPLAY_CONFIG_PATH)


def load_tsc2_replay_config() -> dict[str, Any]:
    return load_yaml(TSC2_REPLAY_CONFIG_PATH)


def load_crebbp_replay_config() -> dict[str, Any]:
    return load_yaml(CREBBP_REPLAY_CONFIG_PATH)
