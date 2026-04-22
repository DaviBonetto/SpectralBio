"""SpectralBio public replay, verification, and audit CLI."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any

from spectralbio.adapt import create_adaptation_scaffold
from spectralbio.applicability import evaluate_applicability
from spectralbio.benchmark_registry import list_targets
from spectralbio.constants import (
    CANONICAL_OUTPUT_DIR,
    PAPER_OUTPUT_DIR,
    PROJECT_ROOT,
    REGENERATION_OUTPUT_DIR,
    RELEASE_DIR,
    REPLAY_OUTPUT_DIR,
    STATUS_OUTPUT_DIR,
    TRANSFER_OUTPUT_DIR,
)
from spectralbio.preflight import run_doctor, run_preflight
from spectralbio.pipeline.run_canonical import run as run_canonical
from spectralbio.pipeline.run_transfer import run as run_transfer
from spectralbio.pipeline.verify import verify_run_outputs
from spectralbio.regeneration import regenerate_surface, regenerate_target, reproduce_all
from spectralbio.replay import run_replay_audit, run_replay_target
from spectralbio.stats_report import build_stats_report
from spectralbio.status import build_status_payload, new_run_id, status_stdout, write_status_bundle
from spectralbio.sensitivity import build_sensitivity_report
from spectralbio.utils.io import ensure_dir, read_json
from spectralbio.verification import verify_target_bundle


def _emit_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2))


def _reset_dir(path: Path) -> Path:
    shutil.rmtree(path, ignore_errors=True)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _default_cache_dir() -> Path:
    return PROJECT_ROOT / ".cache" / "spectralbio"


def _copy_release_contract_files(destination_dir: Path) -> tuple[list[str], list[str]]:
    files_to_copy = (
        ("README.md", "README.md"),
        ("SKILL.md", "SKILL.md"),
        ("abstract.md", "abstract.md"),
        ("content.md", "content.md"),
        ("docs/truth_contract.md", "docs/truth_contract.md"),
        ("docs/reproducibility.md", "docs/reproducibility.md"),
        ("claw_agent_guide.md", "claw_agent_guide.md"),
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
        ("schemas", "schemas"),
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
        ("benchmarks/benchmark_registry.json", "benchmarks/benchmark_registry.json"),
    )
    for source_relative, destination_relative in file_copies:
        source = PROJECT_ROOT / source_relative
        destination = destination_dir / destination_relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        copied_files.append(destination_relative)

    for target in ("brca2", "tsc2", "crebbp"):
        source = PROJECT_ROOT / "benchmarks" / target
        destination = destination_dir / "benchmarks" / target
        shutil.copytree(source, destination, dirs_exist_ok=True)
        copied_files.append(f"benchmarks/{target}")

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
    if REPLAY_OUTPUT_DIR.exists():
        shutil.copytree(REPLAY_OUTPUT_DIR, release_outputs / "replay", dirs_exist_ok=True)
    return {
        "status": "PASS",
        "release_dir": str(destination_dir),
        "verification": verification,
        "support_files": support_files,
        "support_trees": support_trees,
        "hf_space": hf_space,
        "hf_dataset": hf_dataset,
    }


def _add_execution_flags(parser: argparse.ArgumentParser, *, include_output_dir: bool = True) -> None:
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")
    if include_output_dir:
        parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--cache-dir", type=Path, default=_default_cache_dir())
    parser.add_argument("--timeout", type=int, default=0)
    parser.add_argument("--cpu-only", action="store_true")
    parser.add_argument("--offline", action="store_true")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="spectralbio",
        description="SpectralBio public replay, verification, and scientific audit CLI",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    canonical = subparsers.add_parser(
        "canonical",
        help="Materialize the frozen TP53 canonical replay surface",
    )
    _add_execution_flags(canonical, include_output_dir=False)
    canonical.add_argument("--output-dir", type=Path, default=CANONICAL_OUTPUT_DIR)

    transfer = subparsers.add_parser(
        "transfer",
        help="Materialize the bounded BRCA1 auxiliary transfer artifact",
    )
    _add_execution_flags(transfer, include_output_dir=False)
    transfer.add_argument("--output-dir", type=Path, default=TRANSFER_OUTPUT_DIR)

    verify = subparsers.add_parser(
        "verify",
        help="Verify a replay target bundle or, without --target, preserve the legacy TP53/BRCA1 contract check",
    )
    _add_execution_flags(verify, include_output_dir=False)
    verify.add_argument("--canonical-dir", type=Path, default=CANONICAL_OUTPUT_DIR)
    verify.add_argument("--transfer-dir", type=Path, default=TRANSFER_OUTPUT_DIR)
    verify.add_argument("--target", choices=["tp53", "brca2", "tsc2", "crebbp"])

    verify_legacy = subparsers.add_parser(
        "verify-legacy",
        help="Validate the original TP53 canonical plus bounded BRCA1 transfer contract",
    )
    _add_execution_flags(verify_legacy, include_output_dir=False)
    verify_legacy.add_argument("--canonical-dir", type=Path, default=CANONICAL_OUTPUT_DIR)
    verify_legacy.add_argument("--transfer-dir", type=Path, default=TRANSFER_OUTPUT_DIR)

    preflight = subparsers.add_parser("preflight", help="Check environment, frozen assets, schemas, and offline replay readiness")
    _add_execution_flags(preflight, include_output_dir=False)
    preflight.add_argument("--output-dir", type=Path, default=REPLAY_OUTPUT_DIR)

    doctor = subparsers.add_parser("doctor", help="Emit a structured diagnosis bundle with exact recovery guidance")
    _add_execution_flags(doctor, include_output_dir=False)
    doctor.add_argument("--output-dir", type=Path, default=REPLAY_OUTPUT_DIR)

    replay = subparsers.add_parser("replay", help="Run one frozen replay benchmark surface and validate it immediately")
    _add_execution_flags(replay, include_output_dir=False)
    replay.add_argument("--target", choices=["tp53", "brca2", "tsc2", "crebbp"], required=True)
    replay.add_argument("--output-dir", type=Path)

    replay_audit = subparsers.add_parser("replay-audit", help="Run all frozen replay targets and emit an aggregate replay summary")
    _add_execution_flags(replay_audit, include_output_dir=False)
    replay_audit.add_argument("--output-dir", type=Path, default=REPLAY_OUTPUT_DIR)

    stats_report = subparsers.add_parser("stats-report", help="Emit a structured statistical summary for TP53 or BRCA2")
    _add_execution_flags(stats_report, include_output_dir=False)
    stats_report.add_argument("--target", choices=["tp53", "brca2"], required=True)
    stats_report.add_argument("--output-dir", type=Path)

    sensitivity = subparsers.add_parser("sensitivity", help="Emit bounded predefined sensitivity grids without widening claims")
    _add_execution_flags(sensitivity, include_output_dir=False)
    sensitivity.add_argument("--target", choices=["tp53", "brca2"], required=True)
    sensitivity.add_argument("--output-dir", type=Path)

    regenerate = subparsers.add_parser("regenerate", help="Materialize deterministic regeneration bundles for a target or scientific surface")
    _add_execution_flags(regenerate, include_output_dir=False)
    regenerate.add_argument("--target", choices=["tp53", "brca2"])
    regenerate.add_argument("--surface", choices=["scale-repair", "portability", "holdout-control"])
    regenerate.add_argument("--output-dir", type=Path)

    reproduce = subparsers.add_parser("reproduce-all", help="Build the paper-grade deterministic reproduction bundle")
    _add_execution_flags(reproduce, include_output_dir=False)
    reproduce.add_argument("--output-dir", type=Path, default=PAPER_OUTPUT_DIR)

    adapt = subparsers.add_parser("adapt", help="Scaffold a bounded onboarding package for a new target without validating claims")
    _add_execution_flags(adapt, include_output_dir=False)
    adapt.add_argument("--gene", required=True)
    adapt.add_argument("--variants", type=Path, required=True)
    adapt.add_argument("--reference", type=Path, required=True)
    adapt.add_argument("--output-dir", type=Path, default=PROJECT_ROOT / "artifacts" / "onboarding")

    applicability = subparsers.add_parser("applicability", help="Emit bounded applicability diagnostics without certifying transfer success")
    _add_execution_flags(applicability, include_output_dir=False)
    applicability.add_argument("--gene", required=True)
    applicability.add_argument("--variants", type=Path, required=True)
    applicability.add_argument("--reference", type=Path, required=True)
    applicability.add_argument("--output-dir", type=Path, default=PROJECT_ROOT / "artifacts" / "applicability")

    list_targets_cmd = subparsers.add_parser("list-targets", help="List targets with role labels, replay support, verification support, and bounded claim status")
    _add_execution_flags(list_targets_cmd, include_output_dir=False)

    explain = subparsers.add_parser("explain-status", help="Explain PASS or FAIL status and suggest the next command")
    _add_execution_flags(explain, include_output_dir=False)
    explain.add_argument("--path", type=Path, required=True)

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


def _default_mode(args: argparse.Namespace) -> tuple[str, str | None, str]:
    if args.command == "canonical":
        return "canonical", "tp53", "validation_anchor"
    if args.command == "transfer":
        return "transfer", "brca1", "auxiliary_bounded_executable_surface"
    if args.command == "replay":
        target = args.target
        roles = {
            "tp53": "validation_anchor",
            "brca2": "flagship_non_anchor_canonical_target",
            "tsc2": "replay_ready_transfer_surface",
            "crebbp": "replay_ready_transfer_surface",
        }
        return "replay", target, roles[target]
    if args.command == "verify" and getattr(args, "target", None):
        return "verify", args.target, "target_verification"
    if args.command == "verify-legacy":
        return "verify", "tp53_brca1_legacy", "legacy_contract_verification"
    if args.command == "stats-report":
        return "stats-report", args.target, "statistical_audit"
    if args.command == "sensitivity":
        return "sensitivity", args.target, "sensitivity_audit"
    if args.command == "regenerate" and getattr(args, "target", None):
        return "regeneration", args.target, "deterministic_regeneration"
    if args.command == "regenerate" and getattr(args, "surface", None):
        return "regeneration", args.surface, "scientific_audit_surface"
    return args.command, None, args.command


def _dispatch(args: argparse.Namespace) -> dict[str, Any]:
    if args.command == "canonical":
        return run_canonical(args.output_dir)
    if args.command == "transfer":
        return run_transfer(args.output_dir)
    if args.command == "verify":
        if args.target:
            return verify_target_bundle(args.target, (args.output_dir if hasattr(args, "output_dir") and args.output_dir else REPLAY_OUTPUT_DIR / args.target))
        return verify_run_outputs(args.canonical_dir, args.transfer_dir)
    if args.command == "verify-legacy":
        return verify_run_outputs(args.canonical_dir, args.transfer_dir)
    if args.command == "preflight":
        return run_preflight(args.cache_dir, args.output_dir, offline=args.offline, cpu_only=args.cpu_only)
    if args.command == "doctor":
        return run_doctor(args.cache_dir, args.output_dir, offline=args.offline, cpu_only=args.cpu_only)
    if args.command == "replay":
        return run_replay_target(args.target, output_dir=args.output_dir, offline=True, cpu_only=True)
    if args.command == "replay-audit":
        return run_replay_audit(offline=True, cpu_only=True)
    if args.command == "stats-report":
        return build_stats_report(args.target, args.output_dir)
    if args.command == "sensitivity":
        return build_sensitivity_report(args.target, args.output_dir)
    if args.command == "regenerate":
        if args.target:
            return regenerate_target(args.target, args.output_dir)
        if args.surface:
            return regenerate_surface(args.surface, args.output_dir)
        raise ValueError("regenerate requires either --target or --surface")
    if args.command == "reproduce-all":
        return reproduce_all(args.output_dir)
    if args.command == "adapt":
        return create_adaptation_scaffold(args.gene, args.variants, args.reference, args.output_dir)
    if args.command == "applicability":
        ensure_dir(args.output_dir)
        return evaluate_applicability(args.gene, args.variants, args.reference, args.output_dir / f"{args.gene.lower()}_applicability.json")
    if args.command == "list-targets":
        return {"status": "PASS", "targets": list_targets()}
    if args.command == "explain-status":
        payload = read_json(args.path)
        diagnosis_path = args.path.parent / "diagnosis.json"
        diagnosis = read_json(diagnosis_path) if diagnosis_path.exists() else None
        target_label = payload.get("target") or "global surface"
        explanation = (
            f"{payload.get('command', 'unknown command')} => {payload.get('status', 'UNKNOWN')} "
            f"for {target_label}; "
            f"surface_role={payload.get('surface_role', 'unknown')}; "
            f"next_action={payload.get('next_action', 'none')}."
        )
        if diagnosis is not None:
            explanation += f" diagnosis_category={diagnosis.get('category', 'unknown')}."
        return {
            "status": "PASS",
            "path": str(args.path),
            "explanation": explanation,
            "status_payload": payload,
            "diagnosis": diagnosis,
        }
    if args.command == "export-hf-space":
        return export_hf_space()
    if args.command == "export-hf-dataset":
        return export_hf_dataset()
    if args.command == "release":
        return release_bundle()
    raise ValueError(f"Unknown command: {args.command}")


def _emit_status_bundle(
    *,
    args: argparse.Namespace,
    argv: list[str] | None,
    payload: dict[str, Any],
    exit_code: int,
    started_at: str,
    duration_seconds: float,
) -> None:
    mode, target, surface_role = _default_mode(args)
    command_text = "spectralbio " + " ".join(argv or sys.argv[1:])
    status_payload = build_status_payload(
        command=command_text.strip(),
        status=payload.get("status", "PASS" if exit_code == 0 else "FAIL"),
        exit_code=exit_code,
        mode=mode,
        target=target,
        surface_role=surface_role,
        started_at=started_at,
        finished_at=datetime.now(timezone.utc).isoformat(),
        duration_seconds=duration_seconds,
        offline=getattr(args, "offline", False),
        cpu_only=getattr(args, "cpu_only", False),
        artifacts_used=payload.get("artifacts_used", []),
        artifacts_emitted=payload.get("artifacts_emitted", []),
        checks_performed=payload.get("checks_performed", []),
        metrics=payload.get("metrics") if isinstance(payload.get("metrics"), dict) else {},
        warnings=payload.get("warnings", []),
        next_action=payload.get("next_action", "none"),
        details={"command": args.command},
    )
    extra_json_files: dict[str, Any] | None = None
    if args.command == "doctor":
        extra_json_files = {"diagnosis.json": payload}
    run_dir = write_status_bundle(
        run_id=new_run_id(args.command.replace("-", "_")),
        payload=status_payload,
        stdout_text=status_stdout(payload),
        stderr_text="" if exit_code == 0 else status_stdout(payload),
        command_text=command_text,
        root_dir=STATUS_OUTPUT_DIR,
        extra_json_files=extra_json_files,
    )
    if args.command == "replay" and target:
        replay_status_path = (args.output_dir or (REPLAY_OUTPUT_DIR / target)) / "status.json"
        replay_status_path.parent.mkdir(parents=True, exist_ok=True)
        replay_status_path.write_text(json.dumps(status_payload, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    started_at = datetime.now(timezone.utc).isoformat()
    timer = perf_counter()
    try:
        payload = _dispatch(args)
        exit_code = 0 if payload.get("status", "PASS") == "PASS" else 1
    except Exception as exc:
        payload = {
            "status": "FAIL",
            "error": str(exc),
            "exception_type": type(exc).__name__,
            "next_action": "Inspect the generated status bundle and fix the reported contract or environment issue.",
        }
        exit_code = 1

    _emit_status_bundle(
        args=args,
        argv=argv,
        payload=payload,
        exit_code=exit_code,
        started_at=started_at,
        duration_seconds=perf_counter() - timer,
    )

    if args.command == "explain-status" and not getattr(args, "json", False):
        print(payload["explanation"])
    else:
        _emit_json(payload)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
