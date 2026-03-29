from __future__ import annotations

from spectralbio.constants import BENCHMARKS_DIR
from spectralbio.data.load_benchmarks import load_brca1_full_filtered, load_brca1_transfer100, load_tp53_variants
from spectralbio.utils.hashing import sha256_file
from spectralbio.utils.io import read_json


def test_manifest_counts_match_dataset_files() -> None:
    tp53_manifest = read_json(BENCHMARKS_DIR / "manifests" / "tp53_canonical_manifest.json")
    brca1_manifest = read_json(BENCHMARKS_DIR / "manifests" / "brca1_transfer_manifest.json")

    assert tp53_manifest["count"] == len(load_tp53_variants())
    assert brca1_manifest["count"] == len(load_brca1_transfer100())
    assert len(load_brca1_full_filtered()) >= len(load_brca1_transfer100())


def test_manifest_roles_are_explicit() -> None:
    tp53_manifest = read_json(BENCHMARKS_DIR / "manifests" / "tp53_canonical_manifest.json")
    brca1_manifest = read_json(BENCHMARKS_DIR / "manifests" / "brca1_transfer_manifest.json")
    assert tp53_manifest["role"] == "canonical_benchmark"
    assert brca1_manifest["role"] == "secondary_bounded_transfer"


def test_checksum_registry_matches_frozen_dataset_files() -> None:
    checksums = read_json(BENCHMARKS_DIR / "manifests" / "checksums.json")

    assert checksums["benchmarks/tp53/tp53_canonical_v1.json"] == sha256_file(
        BENCHMARKS_DIR / "tp53" / "tp53_canonical_v1.json"
    )
    assert checksums["benchmarks/tp53/tp53_scores_v1.json"] == sha256_file(
        BENCHMARKS_DIR / "tp53" / "tp53_scores_v1.json"
    )
    assert checksums["benchmarks/brca1/brca1_transfer100_v1.json"] == sha256_file(
        BENCHMARKS_DIR / "brca1" / "brca1_transfer100_v1.json"
    )
    assert checksums["benchmarks/brca1/brca1_full_filtered_v1.json"] == sha256_file(
        BENCHMARKS_DIR / "brca1" / "brca1_full_filtered_v1.json"
    )
    assert checksums["benchmarks/sequences/tp53.fasta"] == sha256_file(
        BENCHMARKS_DIR / "sequences" / "tp53.fasta"
    )
    assert checksums["benchmarks/sequences/brca1.fasta"] == sha256_file(
        BENCHMARKS_DIR / "sequences" / "brca1.fasta"
    )


def test_transfer_provenance_is_explicit() -> None:
    brca1_manifest = read_json(BENCHMARKS_DIR / "manifests" / "brca1_transfer_manifest.json")
    source_snapshot = read_json(BENCHMARKS_DIR / "manifests" / "source_snapshot.json")
    provenance_dataset = source_snapshot["provenance_only_datasets"]["brca1_full_filtered_v1"]
    derived_dataset = source_snapshot["derived_datasets"]["brca1_transfer100_v1"]

    assert provenance_dataset["role"] == "provenance_only"
    assert provenance_dataset["count"] == len(load_brca1_full_filtered())
    assert brca1_manifest["source_dataset"]["role"] == "provenance_only"
    assert brca1_manifest["source_dataset"]["count"] == len(load_brca1_full_filtered())
    assert derived_dataset["count"] == len(load_brca1_transfer100())
    assert derived_dataset["derived_from"] == provenance_dataset["file"]
    assert derived_dataset["selection_rule"] == brca1_manifest["source_dataset"]["selection_rule"]


def test_transfer_dataset_is_the_fixed_first100_subset() -> None:
    assert load_brca1_transfer100() == load_brca1_full_filtered()[:100]
