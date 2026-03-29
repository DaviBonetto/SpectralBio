"""Verification logic for canonical and transfer outputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from spectralbio.constants import (
    BRCA1_FULL_FILTERED_PATH,
    BRCA1_TRANSFER_CONFIG_PATH,
    BRCA1_TRANSFER100_PATH,
    CANONICAL_COMMAND,
    CHECKSUMS_PATH,
    REQUIRED_TRANSFER_PHRASE,
    TP53_BENCHMARK_MANIFEST_PATH,
    TP53_CANONICAL_PATH,
    TP53_CONFIG_PATH,
    TP53_SCORE_REFERENCE_PATH,
    TRANSFER_COMMAND,
)
from spectralbio.data.load_benchmarks import (
    load_brca1_full_filtered,
    load_expected_files,
    load_expected_metrics,
    load_output_schema,
    load_tp53_scores,
    load_verification_rules,
)
from spectralbio.utils.hashing import file_metadata, sha256_file
from spectralbio.utils.io import project_relpath, read_json, read_tsv, write_json

NEGATION_MARKERS = (
    "no ",
    "not ",
    "without ",
    "forbidden",
    "prohibited",
    "avoid ",
    "do not ",
    "don't ",
    "never ",
)


def _close_enough(left: float, right: float, tolerance: float) -> bool:
    return abs(left - right) <= tolerance


def _actual_file_set(directory: Path) -> list[str]:
    return sorted(path.name for path in directory.iterdir() if path.is_file())


def _required_fields(section_name: str) -> list[str]:
    return list(load_output_schema()["properties"][section_name]["required"])


def _missing_fields(payload: dict[str, Any], section_name: str) -> list[str]:
    return [field for field in _required_fields(section_name) if field not in payload]


def _record_check(checks: dict[str, bool], errors: list[str], name: str, passed: bool, message: str) -> None:
    checks[name] = passed
    if not passed:
        errors.append(message)


def _canonical_report(canonical_dir: Path) -> dict[str, Any]:
    expected_files = load_expected_files()["canonical_run"]
    expected_metrics = load_expected_metrics()["canonical"]
    rules = load_verification_rules()
    tolerance = float(rules["metric_tolerance"])

    checks: dict[str, bool] = {}
    errors: list[str] = []

    try:
        run_metadata = read_json(canonical_dir / "run_metadata.json")
        inputs_manifest = read_json(canonical_dir / "inputs_manifest.json")
        metrics_payload = read_json(canonical_dir / "tp53_metrics.json")
        summary = read_json(canonical_dir / "summary.json")
        manifest = read_json(canonical_dir / "manifest.json")
        score_rows = read_tsv(canonical_dir / "tp53_scores.tsv")
        figure_meta = file_metadata(canonical_dir / "roc_tp53.png")
    except FileNotFoundError as exc:
        return {
            "status": "FAIL",
            "checks": {"required_files_present": False},
            "errors": [f"Missing canonical artifact: {exc.filename}"],
        }

    _record_check(
        checks,
        errors,
        "exact_file_set",
        _actual_file_set(canonical_dir) == sorted(expected_files),
        f"Canonical output file set drifted from {expected_files}.",
    )
    _record_check(
        checks,
        errors,
        "run_metadata_schema",
        not _missing_fields(run_metadata, "canonical_run_metadata"),
        "Canonical run_metadata.json is missing required fields.",
    )
    _record_check(
        checks,
        errors,
        "inputs_manifest_schema",
        not _missing_fields(inputs_manifest, "canonical_inputs_manifest"),
        "Canonical inputs_manifest.json is missing required fields.",
    )
    _record_check(
        checks,
        errors,
        "metrics_schema",
        not _missing_fields(metrics_payload, "canonical_metrics"),
        "Canonical tp53_metrics.json is missing required fields.",
    )
    _record_check(
        checks,
        errors,
        "summary_schema",
        not _missing_fields(summary, "canonical_summary"),
        "Canonical summary.json is missing required fields.",
    )
    _record_check(
        checks,
        errors,
        "manifest_schema",
        not _missing_fields(manifest, "canonical_manifest"),
        "Canonical manifest.json is missing required fields.",
    )
    _record_check(
        checks,
        errors,
        "manifest_role",
        manifest.get("role") == "canonical_benchmark",
        "Canonical manifest role must be canonical_benchmark.",
    )
    _record_check(
        checks,
        errors,
        "summary_role",
        summary.get("role") == "canonical_benchmark",
        "Canonical summary role must be canonical_benchmark.",
    )
    _record_check(
        checks,
        errors,
        "primary_claim",
        summary.get("primary_claim") == rules["claims"]["canonical_primary_claim"]
        and manifest.get("primary_claim") == rules["claims"]["canonical_primary_claim"],
        "Canonical primary claim drifted from the truth contract.",
    )
    _record_check(
        checks,
        errors,
        "canonical_command",
        run_metadata.get("command") == CANONICAL_COMMAND and summary.get("command") == CANONICAL_COMMAND,
        "Canonical command drifted from the single canonical CLI path.",
    )
    _record_check(
        checks,
        errors,
        "canonical_config_path",
        run_metadata.get("config_path") == project_relpath(TP53_CONFIG_PATH)
        and summary.get("config_path") == project_relpath(TP53_CONFIG_PATH)
        and manifest.get("config_path") == project_relpath(TP53_CONFIG_PATH),
        "Canonical config_path drifted from configs/tp53_canonical.yaml.",
    )
    _record_check(
        checks,
        errors,
        "variants_source",
        inputs_manifest.get("variants_source") == project_relpath(TP53_CANONICAL_PATH)
        and summary.get("source_variants") == project_relpath(TP53_CANONICAL_PATH)
        and manifest.get("source_variants") == project_relpath(TP53_CANONICAL_PATH),
        "Canonical TP53 variants source drifted.",
    )
    _record_check(
        checks,
        errors,
        "score_reference_source",
        inputs_manifest.get("score_reference_source") == project_relpath(TP53_SCORE_REFERENCE_PATH)
        and manifest.get("score_reference_source") == project_relpath(TP53_SCORE_REFERENCE_PATH),
        "Canonical TP53 score reference source drifted.",
    )
    _record_check(
        checks,
        errors,
        "benchmark_manifest_source",
        inputs_manifest.get("benchmark_manifest") == project_relpath(TP53_BENCHMARK_MANIFEST_PATH)
        and manifest.get("benchmark_manifest") == project_relpath(TP53_BENCHMARK_MANIFEST_PATH),
        "Canonical benchmark manifest pointer drifted.",
    )
    _record_check(
        checks,
        errors,
        "checksums_ref",
        inputs_manifest.get("checksums_ref") == project_relpath(CHECKSUMS_PATH),
        "Canonical checksums reference drifted.",
    )
    _record_check(
        checks,
        errors,
        "variants_sha256",
        inputs_manifest.get("variants_sha256") == sha256_file(TP53_CANONICAL_PATH),
        "Canonical TP53 variants SHA256 drifted.",
    )
    _record_check(
        checks,
        errors,
        "score_reference_sha256",
        inputs_manifest.get("score_reference_sha256") == sha256_file(TP53_SCORE_REFERENCE_PATH),
        "Canonical TP53 score reference SHA256 drifted.",
    )
    _record_check(
        checks,
        errors,
        "variant_count",
        inputs_manifest.get("n_variants") == expected_metrics["n_total"]
        and summary.get("n_total") == expected_metrics["n_total"]
        and len(score_rows) == expected_metrics["n_total"],
        "Canonical TP53 counts drifted from the frozen expected total.",
    )
    _record_check(
        checks,
        errors,
        "score_rows_match_frozen_reference",
        score_rows == [{key: str(value) for key, value in row.items()} for row in load_tp53_scores()],
        "tp53_scores.tsv no longer matches the frozen score reference rows.",
    )
    summary_metrics = summary.get("metrics", {})
    computed_auc_match = (
        _close_enough(
            float(metrics_payload["computed_auc_best_pair"]),
            float(expected_metrics["auc_best_pair"]),
            tolerance,
        )
        and _close_enough(
            float(summary_metrics["computed_auc_best_pair"]),
            float(expected_metrics["auc_best_pair"]),
            tolerance,
        )
    )
    official_auc_match = (
        _close_enough(
            float(metrics_payload["official_auc_best_pair"]),
            float(expected_metrics["auc_best_pair"]),
            tolerance,
        )
        and _close_enough(
            float(summary_metrics["official_auc_best_pair"]),
            float(expected_metrics["auc_best_pair"]),
            tolerance,
        )
    )
    summary_metrics_match = metrics_payload == summary_metrics
    _record_check(
        checks,
        errors,
        "computed_auc_match",
        computed_auc_match,
        "Canonical computed AUC drifted from the frozen expected value.",
    )
    _record_check(
        checks,
        errors,
        "official_auc_match",
        official_auc_match,
        "Canonical official AUC drifted from the frozen expected value.",
    )
    _record_check(
        checks,
        errors,
        "summary_metrics_match",
        summary_metrics_match,
        "Canonical summary metrics no longer mirror tp53_metrics.json.",
    )
    _record_check(
        checks,
        errors,
        "metrics_match",
        computed_auc_match and official_auc_match and summary_metrics_match,
        "Canonical metrics drifted from the frozen expected values.",
    )
    _record_check(
        checks,
        errors,
        "artifacts_list",
        summary.get("artifacts") == expected_files and manifest.get("artifacts") == expected_files,
        "Canonical artifact list drifted from the frozen output contract.",
    )
    _record_check(
        checks,
        errors,
        "figure_nonempty",
        int(figure_meta["bytes"]) > 0,
        "roc_tp53.png is empty.",
    )

    return {"status": "PASS" if not errors else "FAIL", "checks": checks, "errors": errors}


def _transfer_report(transfer_dir: Path) -> dict[str, Any]:
    expected_files = load_expected_files()["transfer_run"]
    expected_metrics = load_expected_metrics()["transfer"]
    rules = load_verification_rules()
    tolerance = float(rules["metric_tolerance"])

    checks: dict[str, bool] = {}
    errors: list[str] = []

    try:
        summary = read_json(transfer_dir / "summary.json")
        manifest = read_json(transfer_dir / "manifest.json")
        variants = read_json(transfer_dir / "variants.json")
    except FileNotFoundError as exc:
        return {
            "status": "FAIL",
            "checks": {"required_files_present": False},
            "errors": [f"Missing transfer artifact: {exc.filename}"],
        }

    frozen_full = load_brca1_full_filtered()
    _record_check(
        checks,
        errors,
        "exact_file_set",
        _actual_file_set(transfer_dir) == sorted(expected_files),
        f"Transfer output file set drifted from {expected_files}.",
    )
    _record_check(
        checks,
        errors,
        "summary_schema",
        not _missing_fields(summary, "transfer_summary"),
        "Transfer summary.json is missing required fields.",
    )
    _record_check(
        checks,
        errors,
        "manifest_schema",
        not _missing_fields(manifest, "transfer_manifest"),
        "Transfer manifest.json is missing required fields.",
    )
    _record_check(
        checks,
        errors,
        "transfer_role",
        summary.get("role") == "secondary_bounded_transfer"
        and manifest.get("role") == "secondary_bounded_transfer",
        "Transfer role must be secondary_bounded_transfer.",
    )
    _record_check(
        checks,
        errors,
        "secondary_claim",
        summary.get("secondary_claim") == rules["claims"]["transfer_secondary_claim"]
        and manifest.get("secondary_claim") == rules["claims"]["transfer_secondary_claim"],
        "Transfer secondary claim drifted from the truth contract.",
    )
    _record_check(
        checks,
        errors,
        "transfer_command",
        summary.get("command") == TRANSFER_COMMAND,
        "Transfer command drifted from the canonical CLI path.",
    )
    _record_check(
        checks,
        errors,
        "transfer_config_path",
        summary.get("config_path") == project_relpath(BRCA1_TRANSFER_CONFIG_PATH)
        and manifest.get("config_path") == project_relpath(BRCA1_TRANSFER_CONFIG_PATH),
        "Transfer config_path drifted from configs/brca1_transfer.yaml.",
    )
    _record_check(
        checks,
        errors,
        "transfer_variants_source",
        summary.get("source_variants") == project_relpath(BRCA1_TRANSFER100_PATH)
        and manifest.get("source_variants") == project_relpath(BRCA1_TRANSFER100_PATH),
        "Transfer variants source drifted from the frozen BRCA1 transfer100 subset.",
    )
    _record_check(
        checks,
        errors,
        "transfer_provenance_source",
        manifest.get("source_provenance") == project_relpath(BRCA1_FULL_FILTERED_PATH),
        "Transfer provenance source drifted from the frozen BRCA1 full filtered file.",
    )
    _record_check(
        checks,
        errors,
        "transfer_selection_rule",
        manifest.get("selection_rule") == rules["paths"]["transfer_selection_rule"],
        "Transfer selection rule drifted.",
    )
    _record_check(
        checks,
        errors,
        "scope_note",
        summary.get("scope_note") == REQUIRED_TRANSFER_PHRASE,
        "Transfer scope note drifted from the required bounded-transfer phrase.",
    )
    _record_check(
        checks,
        errors,
        "transfer_count",
        summary.get("n_total") == expected_metrics["n_total"]
        and manifest.get("expected_variant_count") == expected_metrics["n_total"]
        and len(variants) == expected_metrics["n_total"],
        "Transfer output count drifted from the frozen expected total.",
    )
    _record_check(
        checks,
        errors,
        "transfer_metric",
        _close_enough(float(summary["metrics"]["official_ll_proper_auc"]), float(expected_metrics["ll_proper_auc"]), tolerance),
        "Transfer official_ll_proper_auc drifted from the frozen expected value.",
    )
    _record_check(
        checks,
        errors,
        "transfer_artifacts",
        summary.get("artifacts") == expected_files and manifest.get("artifacts") == expected_files,
        "Transfer artifact list drifted from the frozen output contract.",
    )
    _record_check(
        checks,
        errors,
        "transfer_matches_fixed_subset",
        variants == frozen_full[: expected_metrics["n_total"]],
        "Transfer variants.json no longer matches the frozen first-100 subset.",
    )
    _record_check(
        checks,
        errors,
        "transfer_not_full_filtered",
        variants != frozen_full,
        "Transfer variants.json matches the full BRCA1 filtered dataset instead of the fixed subset.",
    )

    return {"status": "PASS" if not errors else "FAIL", "checks": checks, "errors": errors}


def build_partial_verification_report(canonical_dir: Path) -> dict[str, Any]:
    canonical = _canonical_report(canonical_dir)
    return {
        "status": canonical["status"],
        "canonical": canonical,
        "transfer": {"status": "PENDING", "checks": {}, "errors": []},
    }


def verify_run_outputs(canonical_dir: Path, transfer_dir: Path) -> dict[str, Any]:
    canonical = _canonical_report(canonical_dir)
    transfer = _transfer_report(transfer_dir)
    report = {
        "status": "PASS" if canonical["status"] == "PASS" and transfer["status"] == "PASS" else "FAIL",
        "canonical": canonical,
        "transfer": transfer,
    }
    if canonical_dir.exists():
        write_json(canonical_dir / "verification.json", report)
    return report


def _contains_unnegated_phrase(contents: str, phrase: str) -> bool:
    normalized_phrase = phrase.lower()
    for raw_line in contents.splitlines():
        line = raw_line.lower()
        search_from = 0
        while True:
            hit_index = line.find(normalized_phrase, search_from)
            if hit_index == -1:
                break
            prefix = line[max(0, hit_index - 48) : hit_index]
            if not any(marker in prefix for marker in NEGATION_MARKERS):
                return True
            search_from = hit_index + len(normalized_phrase)
    return False


def verify_text_contract(paths: list[Path]) -> dict[str, Any]:
    rules = load_verification_rules()
    findings: dict[str, Any] = {"forbidden_hits": [], "required_phrase_present": False}
    contents = "\n".join(path.read_text(encoding="utf-8") for path in paths if path.exists()).lower()

    for phrase in rules["text_contract"]["forbidden_generalization_phrases"]:
        if _contains_unnegated_phrase(contents, phrase):
            findings["forbidden_hits"].append(phrase)

    findings["required_phrase_present"] = REQUIRED_TRANSFER_PHRASE.lower() in contents
    return findings
