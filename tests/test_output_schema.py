from __future__ import annotations

import json

from spectralbio.constants import OUTPUT_SCHEMA_PATH, VERIFICATION_RULES_PATH
from spectralbio.pipeline.run_canonical import run as run_canonical
from spectralbio.pipeline.run_transfer import run as run_transfer
from spectralbio.pipeline.verify import verify_run_outputs
from spectralbio.utils.io import read_json


def test_output_schema_defines_canonical_and_transfer_sections() -> None:
    schema = read_json(OUTPUT_SCHEMA_PATH)
    assert "canonical_run_metadata" in schema["properties"]
    assert "canonical_inputs_manifest" in schema["properties"]
    assert "canonical_metrics" in schema["properties"]
    assert "canonical_summary" in schema["properties"]
    assert "canonical_manifest" in schema["properties"]
    assert "canonical_verification" in schema["properties"]
    assert "transfer_summary" in schema["properties"]
    assert "transfer_manifest" in schema["properties"]


def test_verification_rules_require_bounded_transfer_language() -> None:
    rules = read_json(VERIFICATION_RULES_PATH)
    required_phrase = rules["text_contract"]["required_transfer_phrase"]
    assert "bounded transfer" in required_phrase.lower()


def test_verify_run_outputs_passes_for_pristine_outputs(tmp_path) -> None:
    canonical_dir = tmp_path / "canonical"
    transfer_dir = tmp_path / "transfer"

    run_canonical(canonical_dir)
    run_transfer(transfer_dir)
    report = verify_run_outputs(canonical_dir, transfer_dir)

    assert report["status"] == "PASS"
    assert report["canonical"]["status"] == "PASS"
    assert report["transfer"]["status"] == "PASS"


def test_verify_run_outputs_fails_loudly_on_metric_drift(tmp_path) -> None:
    canonical_dir = tmp_path / "canonical"
    transfer_dir = tmp_path / "transfer"

    run_canonical(canonical_dir)
    run_transfer(transfer_dir)
    summary_path = canonical_dir / "summary.json"
    payload = read_json(summary_path)
    payload["metrics"]["computed_auc_best_pair"] = 0.1234
    summary_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    report = verify_run_outputs(canonical_dir, transfer_dir)

    assert report["status"] == "FAIL"
    assert report["canonical"]["status"] == "FAIL"
    assert report["canonical"]["checks"]["computed_auc_match"] is False


def test_verify_run_outputs_fails_on_extra_canonical_file(tmp_path) -> None:
    canonical_dir = tmp_path / "canonical"
    transfer_dir = tmp_path / "transfer"

    run_canonical(canonical_dir)
    run_transfer(transfer_dir)
    (canonical_dir / "unexpected.txt").write_text("drift\n", encoding="utf-8")

    report = verify_run_outputs(canonical_dir, transfer_dir)

    assert report["status"] == "FAIL"
    assert report["canonical"]["status"] == "FAIL"
    assert report["canonical"]["checks"]["exact_file_set"] is False
