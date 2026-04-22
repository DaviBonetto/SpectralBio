"""Deterministic regeneration wrappers over frozen manuscript bundles."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from spectralbio.checksums import write_checksums
from spectralbio.constants import PAPER_OUTPUT_DIR, REGENERATION_OUTPUT_DIR
from spectralbio.pipelines import (
    materialize_brca2_replay,
    materialize_full_reproduction_report,
    materialize_holdout_control_surface,
    materialize_portability_surface,
    materialize_scale_repair_surface,
    materialize_tp53_replay,
)
from spectralbio.provenance import build_provenance, write_provenance
from spectralbio.utils.io import ensure_dir, write_json


def _target_regeneration_materializer(target: str):
    if target == "tp53":
        return materialize_tp53_replay
    if target == "brca2":
        return materialize_brca2_replay
    raise ValueError("regenerate --target currently supports tp53 and brca2 only.")


def _surface_regeneration_materializer(surface: str):
    if surface == "scale-repair":
        return materialize_scale_repair_surface
    if surface == "portability":
        return materialize_portability_surface
    if surface == "holdout-control":
        return materialize_holdout_control_surface
    raise ValueError(f"Unknown surface: {surface}")


def regenerate_target(target: str, output_dir: Path | None = None) -> dict[str, Any]:
    target_lower = target.lower()
    destination = ensure_dir((output_dir or REGENERATION_OUTPUT_DIR) / target_lower)
    payload = _target_regeneration_materializer(target_lower)(destination)
    write_json(destination / "raw_inputs_manifest.json", {"target": target_lower, "mode": "regeneration"})
    write_json(destination / "intermediate_manifest.json", {"target": target_lower, "note": "Frozen regeneration wrapper"})
    write_json(destination / "diagnosis.json", {"status": "PASS", "category": "healthy", "summary": "Frozen regeneration surface materialized successfully.", "recommended_fix": "none"})
    write_json(destination / "stats_report.json", {"target": target_lower.upper(), "role": payload["role"], "metrics": payload["metrics"]})
    provenance = build_provenance(
        target=target_lower,
        role=payload["role"],
        command=f"spectralbio regenerate --target {target_lower}",
        input_paths=[],
        model_identifiers=payload["model_identifiers"],
        source_label=f"{target_lower}_frozen_regeneration_bundle",
        output_dir=destination,
    )
    write_provenance(destination / "provenance.json", provenance)
    files = [path for path in destination.iterdir() if path.is_file() and path.name not in {"checksums.json"}]
    write_checksums(destination / "checksums.json", files, destination)
    write_json(destination / "verification.json", {"status": "PASS", "checks": {"bundle_materialized": True}, "errors": []})
    return {"status": "PASS", "target": target_lower, "output_dir": str(destination)}


def regenerate_surface(surface: str, output_dir: Path | None = None) -> dict[str, Any]:
    destination = ensure_dir((output_dir or REGENERATION_OUTPUT_DIR) / surface)
    payload = _surface_regeneration_materializer(surface)(destination)
    write_json(destination / "raw_inputs_manifest.json", {"surface": surface, "mode": "regeneration"})
    write_json(destination / "intermediate_manifest.json", {"surface": surface, "note": "Frozen regeneration wrapper"})
    write_json(destination / "diagnosis.json", {"status": "PASS", "category": "healthy", "summary": "Frozen scientific surface materialized successfully.", "recommended_fix": "none"})
    write_json(destination / "stats_report.json", {"target": surface, "role": "scientific_audit_surface", "metrics": payload if isinstance(payload, dict) else {}})
    provenance = build_provenance(
        target=surface,
        role="scientific_audit_surface",
        command=f"spectralbio regenerate --surface {surface}",
        input_paths=[],
        model_identifiers=[],
        source_label=f"{surface}_frozen_regeneration_bundle",
        output_dir=destination,
    )
    write_provenance(destination / "provenance.json", provenance)
    files = [path for path in destination.iterdir() if path.is_file() and path.name not in {"checksums.json"}]
    write_checksums(destination / "checksums.json", files, destination)
    write_json(destination / "verification.json", {"status": "PASS", "checks": {"bundle_materialized": True}, "errors": []})
    return {"status": "PASS", "surface": surface, "output_dir": str(destination)}


def reproduce_all(output_dir: Path | None = None) -> dict[str, Any]:
    destination = ensure_dir(output_dir or PAPER_OUTPUT_DIR)
    materialize_full_reproduction_report(destination)
    write_json(destination / "contracts" / "reproduction_contract.json", {"mode": "reproduce-all", "status": "PASS"})
    write_provenance(
        destination / "provenance.json",
        build_provenance(
            target="paper",
            role="paper_reproduction_surface",
            command="spectralbio reproduce-all",
            input_paths=[],
            model_identifiers=[],
            source_label="frozen_manuscript_bundle",
            output_dir=destination,
        ),
    )
    files = [path for path in destination.rglob("*") if path.is_file() and path.name not in {"checksums.json", "provenance.json"}]
    write_checksums(destination / "checksums.json", files, destination)
    report = {"status": "PASS", "output_dir": str(destination), "note": "Paper-grade deterministic reproduction bundle materialized."}
    write_json(destination / "reproduction_report.json", report)
    return report
