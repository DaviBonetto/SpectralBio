"""Machine-readable target registry and helpers."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from spectralbio.constants import BENCHMARK_REGISTRY_PATH
from spectralbio.utils.io import read_json


@lru_cache(maxsize=1)
def load_registry() -> dict[str, Any]:
    return read_json(BENCHMARK_REGISTRY_PATH)


def list_targets() -> list[dict[str, Any]]:
    enriched: list[dict[str, Any]] = []
    for entry in load_registry()["targets"]:
        target = entry["target"]
        role = entry["role_label"]
        verification_support = "legacy-only"
        claim_bearing_status = "guardrail"
        notes = entry["source_label"]

        if role in {"validation_anchor", "flagship_non_anchor_canonical_target", "replay_ready_transfer_surface"}:
            verification_support = "replay-target"
        if role == "validation_anchor":
            claim_bearing_status = "yes"
            notes = "default executable anchor"
        elif role == "flagship_non_anchor_canonical_target":
            claim_bearing_status = "yes"
            notes = "flagship non-anchor replay surface"
        elif role == "replay_ready_transfer_surface":
            claim_bearing_status = "bounded_replay_ready"
            notes = "bounded replay-ready transfer surface"
        elif target == "BRCA1":
            notes = "legacy bounded path and negative guardrail"
        elif target == "MSH2":
            verification_support = "guardrail-only"
            notes = "negative portability guardrail"
        elif role == "closure_tribunal_surface":
            verification_support = "regeneration-surface"
            claim_bearing_status = "mixed_boundary"
            notes = "final harsh closure boundary remains mixed"

        enriched.append(
            {
                **entry,
                "verification_support": verification_support,
                "claim_bearing_status": claim_bearing_status,
                "notes": notes,
            }
        )
    return enriched


def get_target(target: str) -> dict[str, Any]:
    target_lower = target.lower()
    for entry in load_registry()["targets"]:
        if entry["target"].lower() == target_lower:
            return entry
    raise KeyError(f"Unknown target: {target}")
