"""SpectralBio public replay and verification CLI."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
from typing import Any

from spectralbio.constants import (
    CANONICAL_OUTPUT_DIR,
    PROJECT_ROOT,
    RELEASE_DIR,
    TRANSFER_OUTPUT_DIR,
)
from spectralbio.pipeline.run_canonical import run as run_canonical
from spectralbio.pipeline.run_transfer import run as run_transfer
from spectralbio.pipeline.verify import verify_run_outputs


def _emit_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2))


def _reset_dir(path: Path) -> Path:
    shutil.rmtree(path, ignore_errors=True)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _copy_release_contract_files(destination_dir: Path) -> tuple[list[str], list[str]]:
    files_to_copy = (
        ("README.md", "README.md"),
        ("SKILL.md", "SKILL.md"),
        ("abstract.md", "abstract.md"),
        ("content.md", "content.md"),
        ("docs/truth_contract.md", "docs/truth_contract.md"),
        ("docs/reproducibility.md", "docs/reproducibility.md"),
        ("benchmarks/manifests/checksums.json", "benchmarks/manifests/checksums.json"),
        ("publish/clawrxiv/spectralbio_clawrxiv.md", "publish/clawrxiv/spectralbio_clawrxiv.md"),
        ("assets/branding/spectralbio_banner.jpeg", "assets/branding/spectralbio_banner.jpeg"),
        ("paper/spectralbio.pdf", "paper/spectralbio.pdf"),
        ("paper/spectralbio.tex", "paper/spectralbio.tex"),
        ("paper/references.bib", "paper/references.bib"),
        ("notebooks/final_accept_part1_support_panel.ipynb", "notebooks/final_accept_part1_support_panel.ipynb"),
        (
            "notebooks/final_accept_part3_esm1v_augmentation_A100.ipynb",
            "notebooks/final_accept_part3_esm1v_augmentation_A100.ipynb",
        ),
        (
            "notebooks/final_accept_part4_brca2_canonicalization_A100.ipynb",
            "notebooks/final_accept_part4_brca2_canonicalization_A100.ipynb",
        ),
        (
            "notebooks/final_accept_part5_protocol_sweep_A100.ipynb",
            "notebooks/final_accept_part5_protocol_sweep_A100.ipynb",
        ),
        (
            "notebooks/final_accept_part6_panel25_brca1_failure_L4.ipynb",
            "notebooks/final_accept_part6_panel25_brca1_failure_L4.ipynb",
        ),
    )
    copied_files: list[str] = []
    for source_relative, destination_relative in files_to_copy:
        source = PROJECT_ROOT / source_relative
        destination = destination_dir / destination_relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        copied_files.append(destination_relative)

    tree_copies = (("paper/assets", "paper/assets"),)
    copied_trees: list[str] = []
    for source_relative, destination_relative in tree_copies:
        source = PROJECT_ROOT / source_relative
        destination = destination_dir / destination_relative
        shutil.copytree(source, destination, dirs_exist_ok=True)
        copied_trees.append(destination_relative)

    return copied_files, copied_trees


def export_hf_space(destination_root: Path | None = None) -> dict[str, Any]:
    destination_dir = (destination_root or RELEASE_DIR) / "hf_space"
    _reset_dir(destination_dir)
    copied_files: list[str] = []

    file_copies = (
        ("publish/hf_space/README.md", "README.md"),
        ("publish/hf_space/requirements.txt", "requirements.txt"),
        ("publish/hf_space/app.py", "publish/hf_space/app.py"),
        ("publish/hf_space/README.md", "publish/hf_space/README.md"),
        ("publish/hf_space/requirements.txt", "publish/hf_space/requirements.txt"),
    )
    for source_relative, destination_relative in file_copies:
        source = PROJECT_ROOT / source_relative
        destination = destination_dir / destination_relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        copied_files.append(destination_relative)

    tree_copies = (
        ("src/spectralbio", "src/spectralbio"),
        ("benchmarks", "benchmarks"),
        ("artifacts/expected", "artifacts/expected"),
    )
    for source_relative, destination_relative in tree_copies:
        source = PROJECT_ROOT / source_relative
        destination = destination_dir / destination_relative
        shutil.copytree(
            source,
            destination,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            dirs_exist_ok=True,
        )
        copied_files.append(destination_relative)

    return {
        "status": "PASS",
        "artifact": "hf_space",
        "destination": str(destination_dir),
        "files": copied_files,
    }


def export_hf_dataset(destination_root: Path | None = None) -> dict[str, Any]:
    destination_dir = (destination_root or RELEASE_DIR) / "hf_dataset"
    _reset_dir(destination_dir)
    copied_files: list[str] = []

    file_copies = (
        ("publish/hf_dataset/README.md", "README.md"),
        ("publish/hf_dataset/dataset_manifest.json", "dataset_manifest.json"),
        ("benchmarks/tp53/tp53_canonical_v1.json", "benchmarks/tp53/tp53_canonical_v1.json"),
        ("benchmarks/tp53/tp53_scores_v1.json", "benchmarks/tp53/tp53_scores_v1.json"),
        ("benchmarks/brca1/brca1_transfer100_v1.json", "benchmarks/brca1/brca1_transfer100_v1.json"),
        ("benchmarks/brca1/brca1_full_filtered_v1.json", "benchmarks/brca1/brca1_full_filtered_v1.json"),
        ("benchmarks/sequences/tp53.fasta", "benchmarks/sequences/tp53.fasta"),
        ("benchmarks/sequences/brca1.fasta", "benchmarks/sequences/brca1.fasta"),
        ("benchmarks/manifests/tp53_canonical_manifest.json", "benchmarks/manifests/tp53_canonical_manifest.json"),
        ("benchmarks/manifests/brca1_transfer_manifest.json", "benchmarks/manifests/brca1_transfer_manifest.json"),
        ("benchmarks/manifests/source_snapshot.json", "benchmarks/manifests/source_snapshot.json"),
        ("benchmarks/manifests/checksums.json", "benchmarks/manifests/checksums.json"),
    )
    for source_relative, destination_relative in file_copies:
        source = PROJECT_ROOT / source_relative
        destination = destination_dir / destination_relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        copied_files.append(destination_relative)
    return {
        "status": "PASS",
        "artifact": "hf_dataset",
        "destination": str(destination_dir),
        "files": copied_files,
    }


def release_bundle(
    destination: Path | None = None,
    canonical_dir: Path = CANONICAL_OUTPUT_DIR,
    transfer_dir: Path = TRANSFER_OUTPUT_DIR,
) -> dict[str, Any]:
    run_canonical(canonical_dir)
    run_transfer(transfer_dir)
    verification = verify_run_outputs(canonical_dir, transfer_dir)
    if verification["status"] != "PASS":
        return {
            "status": "FAIL",
            "release_dir": str(destination or RELEASE_DIR),
            "verification": verification,
        }

    destination_dir = destination or RELEASE_DIR
    _reset_dir(destination_dir)
    support_files, support_trees = _copy_release_contract_files(destination_dir)
    hf_space = export_hf_space(destination_dir)
    hf_dataset = export_hf_dataset(destination_dir)
    release_outputs = destination_dir / "outputs"
    shutil.copytree(canonical_dir, release_outputs / "canonical")
    shutil.copytree(transfer_dir, release_outputs / "transfer")
    return {
        "status": "PASS",
        "release_dir": str(destination_dir),
        "verification": verification,
        "support_files": support_files,
        "support_trees": support_trees,
        "hf_space": hf_space,
        "hf_dataset": hf_dataset,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="spectralbio",
        description="SpectralBio public replay and verification CLI",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    canonical = subparsers.add_parser(
        "canonical",
        help="Materialize the frozen TP53 canonical replay surface",
    )
    canonical.add_argument("--output-dir", type=Path, default=CANONICAL_OUTPUT_DIR)

    transfer = subparsers.add_parser(
        "transfer",
        help="Materialize the bounded BRCA1 auxiliary transfer artifact",
    )
    transfer.add_argument("--output-dir", type=Path, default=TRANSFER_OUTPUT_DIR)

    verify = subparsers.add_parser(
        "verify",
        help="Verify the TP53 replay and BRCA1 auxiliary transfer outputs",
    )
    verify.add_argument("--canonical-dir", type=Path, default=CANONICAL_OUTPUT_DIR)
    verify.add_argument("--transfer-dir", type=Path, default=TRANSFER_OUTPUT_DIR)

    subparsers.add_parser(
        "export-hf-space",
        help="Stage the public HF Space files into the release bundle",
    )
    subparsers.add_parser(
        "export-hf-dataset",
        help="Stage the public HF dataset files into the release bundle",
    )
    subparsers.add_parser("release", help="Build the public replay and audit release bundle")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "canonical":
        payload = run_canonical(args.output_dir)
        _emit_json(payload)
        return 0 if payload["status"] == "PASS" else 1
    if args.command == "transfer":
        payload = run_transfer(args.output_dir)
        _emit_json(payload)
        return 0 if payload["status"] == "PASS" else 1
    if args.command == "verify":
        results = verify_run_outputs(args.canonical_dir, args.transfer_dir)
        _emit_json(results)
        return 0 if results["status"] == "PASS" else 1
    if args.command == "export-hf-space":
        _emit_json(export_hf_space())
        return 0
    if args.command == "export-hf-dataset":
        _emit_json(export_hf_dataset())
        return 0
    if args.command == "release":
        release = release_bundle()
        _emit_json(release)
        return 0 if release["status"] == "PASS" else 1

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
