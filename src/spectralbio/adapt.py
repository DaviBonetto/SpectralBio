"""Bounded target-onboarding scaffold generator."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from spectralbio.utils.io import ensure_dir, write_json, write_text


def create_adaptation_scaffold(gene: str, variants: Path, reference: Path, output_dir: Path) -> dict[str, Any]:
    gene_lower = gene.lower()
    scaffold_dir = ensure_dir(output_dir / gene_lower)
    write_text(
        scaffold_dir / f"{gene_lower}_config.template.yaml",
        "\n".join(
            [
                f"benchmark: {gene.upper()}",
                "role: replay_ready_transfer_surface",
                f"variants_path: {variants}",
                f"reference_path: {reference}",
                f"output_dir: artifacts/onboarding/{gene_lower}",
            ]
        )
        + "\n",
    )
    write_json(
        scaffold_dir / "benchmark_contract.template.json",
        {
            "target": gene.upper(),
            "role": "unvalidated_scaffold",
            "warning": "This scaffold is not evidence of transfer until independently audited.",
        },
    )
    write_json(
        scaffold_dir / "provenance.template.json",
        {
            "target": gene.upper(),
            "variants_path": str(variants),
            "reference_path": str(reference),
            "warning": "Populate with audited hashes and model metadata before promotion.",
        },
    )
    write_text(
        scaffold_dir / "onboarding_checklist.md",
        "\n".join(
            [
                f"# {gene.upper()} Onboarding Checklist",
                "",
                "- Freeze a target-specific benchmark table.",
                "- Freeze a target-specific score reference.",
                "- Add provenance and checksums.",
                "- Audit negative guardrails and claim boundary.",
                "- Do not promote this target before independent verification.",
            ]
        )
        + "\n",
    )
    return {
        "status": "PASS",
        "gene": gene.upper(),
        "scaffold_dir": str(scaffold_dir),
        "warning": "Scaffold only. This does not validate a new target.",
    }
