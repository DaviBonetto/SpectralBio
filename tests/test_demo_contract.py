from __future__ import annotations

from pathlib import Path

import spectralbio.demo.score_variant as demo_contract
from spectralbio.constants import FORBIDDEN_GENERALIZATION_PHRASES


def test_demo_presets_keep_brca1_secondary_labeling() -> None:
    brca1_presets = [name for name in demo_contract.PRESETS if name.startswith("BRCA1")]
    assert brca1_presets
    assert all("secondary" in name.lower() for name in brca1_presets)
    assert demo_contract.DEFAULT_PRESET_NAME.startswith("TP53")
    assert all(
        demo_contract.PRESETS[name]["benchmark_role"] == demo_contract.SECONDARY_BENCHMARK_ROLE
        for name in brca1_presets
    )


def test_demo_metrics_reference_frozen_contract() -> None:
    metrics = demo_contract.official_metrics()
    assert metrics["canonical"]["auc_best_pair"] == 0.7498
    assert metrics["transfer"]["ll_proper_auc"] == 0.9174


def test_demo_metrics_are_returned_as_independent_snapshots() -> None:
    first_metrics = demo_contract.official_metrics()
    first_metrics["canonical"]["auc_best_pair"] = -1.0

    second_metrics = demo_contract.official_metrics()
    assert second_metrics["canonical"]["auc_best_pair"] == 0.7498


def test_demo_metrics_keep_tp53_as_primary_benchmark() -> None:
    metrics = demo_contract.official_metrics()
    assert metrics["canonical"]["benchmark"] == "TP53"


def test_score_variant_contract_has_machine_readable_sections(monkeypatch) -> None:
    def fake_analyze(gene: str, position_0_indexed: int, mutant_aa: str) -> dict[str, object]:
        assert gene == "TP53"
        assert position_0_indexed == 174
        assert mutant_aa == "H"
        return {
            "gene": "TP53",
            "position_1_indexed": 175,
            "position_0_indexed": 174,
            "wt_aa": "R",
            "mut_aa": "H",
            "protein_variant": "p.Arg175His",
            "frob_dist": 1.234567,
            "trace_ratio": 0.111111,
            "sps_log": 0.222222,
            "ll_proper": 0.333333,
            "combined_raw": 0.444444,
            "combined_percentile": 95.0,
            "label": "high pathogenicity signal",
            "label_key": "high_signal",
            "seed": 42,
        }

    monkeypatch.setattr(demo_contract, "analyze_variant", fake_analyze)
    payload = demo_contract.score_variant_contract(
        "TP53",
        174,
        "H",
        preset_name=demo_contract.DEFAULT_PRESET_NAME,
    )

    assert payload["contract_version"] == demo_contract.CONTRACT_VERSION
    assert set(payload) == {
        "contract_version",
        "request",
        "result",
        "benchmark_context",
        "official_metrics",
    }
    assert payload["benchmark_context"]["benchmark_role"] == demo_contract.PRIMARY_BENCHMARK_ROLE
    assert payload["benchmark_context"]["preset"]["is_default_tp53_preset"] is True
    assert payload["result"]["classification"]["label_key"] == "high_signal"
    assert payload["result"]["reference_calibration"]["reference_benchmark"] == "TP53"


def test_score_variant_contract_rejects_mismatched_preset_metadata(monkeypatch) -> None:
    def fake_analyze(gene: str, position_0_indexed: int, mutant_aa: str) -> dict[str, object]:
        assert gene == "TP53"
        assert position_0_indexed == 174
        assert mutant_aa == "H"
        return {
            "gene": "TP53",
            "position_1_indexed": 175,
            "position_0_indexed": 174,
            "wt_aa": "R",
            "mut_aa": "H",
            "protein_variant": "p.Arg175His",
            "frob_dist": 1.234567,
            "trace_ratio": 0.111111,
            "sps_log": 0.222222,
            "ll_proper": 0.333333,
            "combined_raw": 0.444444,
            "combined_percentile": 95.0,
            "label": "high pathogenicity signal",
            "label_key": "high_signal",
            "seed": 42,
        }

    monkeypatch.setattr(demo_contract, "analyze_variant", fake_analyze)
    payload = demo_contract.score_variant_contract(
        "TP53",
        174,
        "H",
        preset_name="BRCA1 | A1708E | secondary bounded transfer example",
    )

    assert payload["request"]["preset_name"] == demo_contract.DEFAULT_PRESET_NAME
    assert payload["benchmark_context"]["preset"]["name"] == demo_contract.DEFAULT_PRESET_NAME
    assert payload["benchmark_context"]["preset"]["is_default_tp53_preset"] is True


def test_space_app_imports_shared_demo_core_only() -> None:
    app_text = Path("publish/hf_space/app.py").read_text(encoding="utf-8")
    assert "import spectralbio.demo.score_variant as demo_contract" in app_text
    assert app_text.count("spectralbio.") == 1
    assert 'api_name="/score_variant"' in app_text
    assert "Combined percentile calibrated against TP53 canonical benchmark" in app_text
    assert "Secondary bounded transfer context remains available in the raw payload only." in app_text


def test_space_surfaces_keep_allowlist_wording_and_drop_legacy_refs() -> None:
    app_text = Path("publish/hf_space/app.py").read_text(encoding="utf-8")
    publish_readme = Path("publish/hf_space/README.md").read_text(encoding="utf-8")
    legacy_readme = Path("huggingface/README.md").read_text(encoding="utf-8")
    combined = "\n".join((app_text, publish_readme, legacy_readme)).lower()

    for phrase in (
        "tp53 canonical executable benchmark",
        "bounded transfer on a fixed brca1 subset (n=100)",
        "secondary transfer evaluation without retraining",
        "adaptation recipe only",
        "research reproducibility artifact",
    ):
        assert phrase in combined

    for phrase in FORBIDDEN_GENERALIZATION_PHRASES:
        assert phrase not in combined

    for stale_reference in ("assets/", "data/", "results_v2.png", "hero_bg.png.png"):
        assert stale_reference not in combined


def test_space_readme_targets_nested_app_and_model_preload() -> None:
    readme = Path("publish/hf_space/README.md").read_text(encoding="utf-8")
    assert "app_file: publish/hf_space/app.py" in readme
    assert "preload_from_hub:" in readme
    assert "facebook/esm2_t30_150M_UR50D" in readme
