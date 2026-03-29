"""Canonical benchmark loaders."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from spectralbio.constants import (
    BRCA1_FULL_FILTERED_PATH,
    BRCA1_TRANSFER100_PATH,
    EXPECTED_FILES_PATH,
    EXPECTED_METRICS_PATH,
    OUTPUT_SCHEMA_PATH,
    TP53_CANONICAL_PATH,
    TP53_SCORE_REFERENCE_PATH,
    VERIFICATION_RULES_PATH,
)
from spectralbio.utils.io import read_json


@lru_cache(maxsize=1)
def load_tp53_variants() -> list[dict[str, Any]]:
    return read_json(TP53_CANONICAL_PATH)


@lru_cache(maxsize=1)
def load_tp53_scores() -> list[dict[str, Any]]:
    return read_json(TP53_SCORE_REFERENCE_PATH)


@lru_cache(maxsize=1)
def load_brca1_full_filtered() -> list[dict[str, Any]]:
    return read_json(BRCA1_FULL_FILTERED_PATH)


@lru_cache(maxsize=1)
def load_brca1_transfer100() -> list[dict[str, Any]]:
    return read_json(BRCA1_TRANSFER100_PATH)


@lru_cache(maxsize=1)
def load_expected_metrics() -> dict[str, Any]:
    return read_json(EXPECTED_METRICS_PATH)


@lru_cache(maxsize=1)
def load_expected_files() -> dict[str, Any]:
    return read_json(EXPECTED_FILES_PATH)


@lru_cache(maxsize=1)
def load_output_schema() -> dict[str, Any]:
    return read_json(OUTPUT_SCHEMA_PATH)


@lru_cache(maxsize=1)
def load_verification_rules() -> dict[str, Any]:
    return read_json(VERIFICATION_RULES_PATH)


def lookup_variant(gene: str, position: int, mut_aa: str) -> dict[str, Any] | None:
    gene_upper = gene.upper()
    mut_upper = mut_aa.upper()
    datasets = [load_tp53_variants(), load_brca1_transfer100(), load_brca1_full_filtered()]
    for dataset in datasets:
        for row in dataset:
            if (
                str(row.get("gene", "")).upper() == gene_upper
                and int(row.get("position", -1)) == position
                and str(row.get("mut_aa", "")).upper() == mut_upper
            ):
                return row
    return None
