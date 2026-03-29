from __future__ import annotations

import json
from pathlib import Path

from spectralbio.cli import build_parser, export_hf_dataset, export_hf_space, main, release_bundle
from spectralbio.pipeline.run_canonical import run as run_canonical
from spectralbio.pipeline.run_transfer import run as run_transfer
from spectralbio.pipeline.verify import verify_run_outputs


def test_cli_exposes_expected_subcommands() -> None:
    parser = build_parser()
    subcommands = parser._subparsers._group_actions[0].choices.keys()
    assert {
        "canonical",
        "transfer",
        "verify",
        "export-hf-space",
        "export-hf-dataset",
        "release",
    }.issubset(set(subcommands))


def test_canonical_and_transfer_runs_create_expected_outputs(tmp_path: Path) -> None:
    canonical_dir = tmp_path / "canonical"
    transfer_dir = tmp_path / "transfer"

    run_canonical(canonical_dir)
    run_transfer(transfer_dir)

    for name in (
        "run_metadata.json",
        "inputs_manifest.json",
        "tp53_scores.tsv",
        "tp53_metrics.json",
        "summary.json",
        "roc_tp53.png",
        "manifest.json",
        "verification.json",
    ):
        assert (canonical_dir / name).exists()
    for name in ("summary.json", "variants.json", "manifest.json"):
        assert (transfer_dir / name).exists()


def test_verify_command_emits_json_and_passes_for_contract_compliant_outputs(tmp_path: Path, capsys) -> None:
    canonical_dir = tmp_path / "canonical"
    transfer_dir = tmp_path / "transfer"

    run_canonical(canonical_dir)
    run_transfer(transfer_dir)

    exit_code = main(["verify", "--canonical-dir", str(canonical_dir), "--transfer-dir", str(transfer_dir)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["status"] == "PASS"
    assert payload["canonical"]["status"] == "PASS"
    assert payload["transfer"]["status"] == "PASS"


def test_export_commands_stage_expected_files() -> None:
    hf_space = export_hf_space()
    hf_dataset = export_hf_dataset()

    assert hf_space["status"] == "PASS"
    assert hf_space["files"] == [
        "README.md",
        "requirements.txt",
        "publish/hf_space/app.py",
        "publish/hf_space/README.md",
        "publish/hf_space/requirements.txt",
        "src/spectralbio",
        "benchmarks",
        "artifacts/expected",
    ]
    destination = Path(hf_space["destination"])
    for relative_path in (
        "README.md",
        "requirements.txt",
        "publish/hf_space/app.py",
        "publish/hf_space/README.md",
        "publish/hf_space/requirements.txt",
        "src/spectralbio/cli.py",
        "benchmarks/tp53/tp53_canonical_v1.json",
        "artifacts/expected/expected_metrics.json",
    ):
        assert (destination / relative_path).exists()
    assert hf_dataset["status"] == "PASS"
    assert hf_dataset["files"] == ["README.md", "dataset_manifest.json"]


def test_release_bundle_copies_support_files_and_verified_outputs(tmp_path: Path) -> None:
    release = release_bundle(destination=tmp_path / "release")
    release_dir = Path(release["release_dir"])

    assert release["status"] == "PASS"
    assert release["verification"]["status"] == "PASS"
    assert release["support_files"] == [
        "README.md",
        "SKILL.md",
        "docs/truth_contract.md",
        "docs/reproducibility.md",
        "benchmarks/manifests/checksums.json",
    ]
    for relative_path in (
        "README.md",
        "SKILL.md",
        "docs/truth_contract.md",
        "docs/reproducibility.md",
        "benchmarks/manifests/checksums.json",
        "hf_space/publish/hf_space/app.py",
        "hf_space/src/spectralbio/cli.py",
        "hf_dataset/README.md",
        "outputs/canonical/summary.json",
        "outputs/transfer/summary.json",
    ):
        assert (release_dir / relative_path).exists()

    verification = verify_run_outputs(release_dir / "outputs" / "canonical", release_dir / "outputs" / "transfer")
    assert verification["status"] == "PASS"
