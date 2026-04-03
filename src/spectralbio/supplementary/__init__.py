"""Supplementary experiment helpers kept outside the canonical contract."""

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
    "BackboneEvaluationConfig",
    "MultiGeneConfig",
    "NestedCVConfig",
    "build_multigene_panel_manifest",
    "create_reject_recovery_paths",
    "create_reject_recovery_zip",
    "run_tp53_backbone_comparison",
    "run_tp53_nested_cv_audit",
    "run_multigene_panel",
    "write_experiment_log",
]
