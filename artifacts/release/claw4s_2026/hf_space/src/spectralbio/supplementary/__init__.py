"""Supplementary experiment helpers kept outside the canonical contract."""

from spectralbio.supplementary.final_accept_hardening import (
    AcceptHardeningConfig,
    build_support_ranked_panel_manifest,
    create_accept_hardening_paths,
    recommend_second_benchmark_candidate,
    run_accept_hardening_suite,
    run_deep_checkpoint_sweep,
    run_gene_nested_cv_audit,
    run_shortlist_gene_nested_cv,
    run_support_ranked_panel,
    scan_clinvar_gene_support,
)
from spectralbio.supplementary.reject_recovery import (
    BackboneEvaluationConfig,
    MultiGeneConfig,
    NestedCVConfig,
    build_multigene_panel_manifest,
    create_reject_recovery_paths,
    create_reject_recovery_zip,
    run_tp53_backbone_comparison,
    run_tp53_nested_cv_audit,
    run_multigene_panel,
    write_experiment_log,
)

__all__ = [
    "AcceptHardeningConfig",
    "BackboneEvaluationConfig",
    "MultiGeneConfig",
    "NestedCVConfig",
    "build_support_ranked_panel_manifest",
    "build_multigene_panel_manifest",
    "create_accept_hardening_paths",
    "create_reject_recovery_paths",
    "create_reject_recovery_zip",
    "recommend_second_benchmark_candidate",
    "run_accept_hardening_suite",
    "run_deep_checkpoint_sweep",
    "run_gene_nested_cv_audit",
    "run_shortlist_gene_nested_cv",
    "run_support_ranked_panel",
    "run_tp53_backbone_comparison",
    "run_tp53_nested_cv_audit",
    "run_multigene_panel",
    "scan_clinvar_gene_support",
    "write_experiment_log",
]
