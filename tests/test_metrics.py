from __future__ import annotations

from spectralbio.data.load_benchmarks import load_expected_metrics, load_tp53_scores, load_verification_rules
from spectralbio.pipeline.evaluate import canonical_metrics


def test_canonical_metrics_match_frozen_expected_auc() -> None:
    computed = canonical_metrics(load_tp53_scores())
    expected = load_expected_metrics()["canonical"]
    tolerance = load_verification_rules()["metric_tolerance"]
    assert abs(computed["auc_best_pair"] - expected["auc_best_pair"]) <= tolerance


def test_expected_metrics_encode_bounded_transfer_language() -> None:
    expected = load_expected_metrics()["transfer"]
    assert expected["n_total"] == 100
    assert "bounded transfer" in expected["wording"].lower()
