from __future__ import annotations

import numpy as np

from spectralbio.data.load_benchmarks import load_tp53_scores
from spectralbio.pipeline.compute_covariance_features import covariance_features
from spectralbio.supplementary.reject_recovery import (
    NestedCVConfig,
    covariance_features_dual,
    create_reject_recovery_paths,
    run_tp53_nested_cv_audit,
)


def test_dual_covariance_features_match_reference_implementation() -> None:
    rng = np.random.default_rng(42)
    hidden_wt = rng.normal(size=(4, 7, 9))
    hidden_mut = rng.normal(size=(4, 7, 9))

    reference = covariance_features(hidden_wt, hidden_mut)
    dual = covariance_features_dual(hidden_wt, hidden_mut)

    for key in ("frob_dist", "trace_ratio", "sps_log"):
        assert np.isclose(reference[key], dual[key], rtol=1e-6, atol=1e-6)


def test_nested_cv_audit_writes_machine_readable_exports(tmp_path) -> None:
    paths = create_reject_recovery_paths(output_root=tmp_path / "supplementary" / "reject_recovery")
    summary = run_tp53_nested_cv_audit(
        paths,
        NestedCVConfig(n_splits=3, n_repeats=2, alpha_step=0.25, random_seed=7, render_figures=False),
        score_rows=list(load_tp53_scores()),
    )

    assert summary["benchmark"] == "TP53 nested CV leakage audit"
    assert (paths.leakage_audit / "tp53_nested_cv_summary.json").exists()
    assert (paths.leakage_audit / "tp53_nested_cv_fold_results.csv").exists()
    assert (paths.leakage_audit / "tp53_nested_cv_alpha_distribution.csv").exists()
    assert (paths.leakage_audit / "tp53_nested_cv_inner_sweeps.json").exists()
