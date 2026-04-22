"""Shared constants and canonical truth for SpectralBio."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BENCHMARKS_DIR = PROJECT_ROOT / "benchmarks"
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
PUBLISH_DIR = PROJECT_ROOT / "publish"
DOCS_DIR = PROJECT_ROOT / "docs"
TEMPORARIO_DIR = PROJECT_ROOT / "temporario"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
CANONICAL_OUTPUT_DIR = OUTPUTS_DIR / "canonical"
TRANSFER_OUTPUT_DIR = OUTPUTS_DIR / "transfer"
REPLAY_OUTPUT_DIR = OUTPUTS_DIR / "replay"
REGENERATION_OUTPUT_DIR = OUTPUTS_DIR / "regeneration"
STATUS_OUTPUT_DIR = OUTPUTS_DIR / "status"
STATS_OUTPUT_DIR = OUTPUTS_DIR / "stats"
PAPER_OUTPUT_DIR = OUTPUTS_DIR / "paper"
RELEASE_DIR = ARTIFACTS_DIR / "release" / "claw4s_2026"
SCHEMAS_DIR = PROJECT_ROOT / "schemas"
DOCKER_DIR = PROJECT_ROOT / "docker"
CI_DIR = PROJECT_ROOT / "ci"
NEW_NOTEBOOK_RESULTS_DIR = PROJECT_ROOT / "New Notebooks" / "results"

TP53_CONFIG_PATH = PROJECT_ROOT / "configs" / "tp53_canonical.yaml"
BRCA1_TRANSFER_CONFIG_PATH = PROJECT_ROOT / "configs" / "brca1_transfer.yaml"
BRCA2_REPLAY_CONFIG_PATH = PROJECT_ROOT / "configs" / "brca2_replay.yaml"
TSC2_REPLAY_CONFIG_PATH = PROJECT_ROOT / "configs" / "tsc2_replay.yaml"
CREBBP_REPLAY_CONFIG_PATH = PROJECT_ROOT / "configs" / "crebbp_replay.yaml"
TP53_BENCHMARK_MANIFEST_PATH = BENCHMARKS_DIR / "manifests" / "tp53_canonical_manifest.json"
BRCA1_TRANSFER_MANIFEST_PATH = BENCHMARKS_DIR / "manifests" / "brca1_transfer_manifest.json"
CHECKSUMS_PATH = BENCHMARKS_DIR / "manifests" / "checksums.json"
BENCHMARK_REGISTRY_PATH = BENCHMARKS_DIR / "benchmark_registry.json"

MODEL_NAME = "facebook/esm2_t30_150M_UR50D"
SEED = 42
WINDOW_RADIUS = 40
ALPHA = 0.55

PRIMARY_CLAIM = "TP53 canonical executable benchmark"
SECONDARY_CLAIM = "bounded transfer on a fixed BRCA1 subset (N=100) without retraining"
ADAPTATION_CLAIM = "adaptation recipe only"
PORTABILITY_CLAIM = "replay-ready multi-target portability across TP53, BRCA2, TSC2, and CREBBP"
PORTABILITY_CLOSURE_BOUNDARY = "the final harsh holdout/control tribunal remains mixed and does not establish model-level closure"

CANONICAL_COMMAND = "spectralbio canonical"
TRANSFER_COMMAND = "spectralbio transfer"
VERIFY_COMMAND = "spectralbio verify"
EXPORT_HF_SPACE_COMMAND = "spectralbio export-hf-space"
EXPORT_HF_DATASET_COMMAND = "spectralbio export-hf-dataset"
RELEASE_COMMAND = "spectralbio release"
PREFLIGHT_COMMAND = "spectralbio preflight"
DOCTOR_COMMAND = "spectralbio doctor"
REPLAY_COMMAND = "spectralbio replay"
REPLAY_AUDIT_COMMAND = "spectralbio replay-audit"
STATS_REPORT_COMMAND = "spectralbio stats-report"
SENSITIVITY_COMMAND = "spectralbio sensitivity"
REGENERATE_COMMAND = "spectralbio regenerate"
REPRODUCE_ALL_COMMAND = "spectralbio reproduce-all"
ADAPT_COMMAND = "spectralbio adapt"
APPLICABILITY_COMMAND = "spectralbio applicability"
LIST_TARGETS_COMMAND = "spectralbio list-targets"
EXPLAIN_STATUS_COMMAND = "spectralbio explain-status"

FORBIDDEN_GENERALIZATION_PHRASES = [
    "any protein",
    "works on any protein",
    "strong cross-protein generalization",
    "exceptional cross-protein generalization",
    "broad cross-protein generalization",
    "exceptional cross-protein transfer",
    "strong generalization",
    "clinical deployment",
    "clinical use",
]

REQUIRED_TRANSFER_PHRASE = (
    "bounded transfer on a fixed BRCA1 subset (N=100) without retraining"
)

WORDING_ALLOWLIST = [
    "TP53 canonical executable benchmark",
    "bounded transfer on a fixed BRCA1 subset (N=100)",
    "secondary transfer evaluation without retraining",
    "adaptation recipe only",
    "research reproducibility artifact",
]

TP53_CANONICAL_PATH = BENCHMARKS_DIR / "tp53" / "tp53_canonical_v1.json"
TP53_SCORE_REFERENCE_PATH = BENCHMARKS_DIR / "tp53" / "tp53_scores_v1.json"
BRCA1_FULL_FILTERED_PATH = BENCHMARKS_DIR / "brca1" / "brca1_full_filtered_v1.json"
BRCA1_TRANSFER100_PATH = BENCHMARKS_DIR / "brca1" / "brca1_transfer100_v1.json"
TP53_SEQUENCE_PATH = BENCHMARKS_DIR / "sequences" / "tp53.fasta"
BRCA1_SEQUENCE_PATH = BENCHMARKS_DIR / "sequences" / "brca1.fasta"
BRCA2_BENCHMARK_DIR = BENCHMARKS_DIR / "brca2"
TSC2_BENCHMARK_DIR = BENCHMARKS_DIR / "tsc2"
CREBBP_BENCHMARK_DIR = BENCHMARKS_DIR / "crebbp"

EXPECTED_METRICS_PATH = ARTIFACTS_DIR / "expected" / "expected_metrics.json"
EXPECTED_FILES_PATH = ARTIFACTS_DIR / "expected" / "expected_files.json"
OUTPUT_SCHEMA_PATH = ARTIFACTS_DIR / "expected" / "output_schema.json"
VERIFICATION_RULES_PATH = ARTIFACTS_DIR / "expected" / "verification_rules.json"

BLOCK1_RESULTS_DIR = NEW_NOTEBOOK_RESULTS_DIR / "01_block1_baseline_alpha_regime_audit_h100"
BLOCK2_RESULTS_DIR = NEW_NOTEBOOK_RESULTS_DIR / "02_block2_failure_mode_hunt_h100"
BLOCK13_RESULTS_DIR = NEW_NOTEBOOK_RESULTS_DIR / "13_block13_multitarget_generalization_closure_h100"
BLOCK14_RESULTS_DIR = NEW_NOTEBOOK_RESULTS_DIR / "14_block14_holdout_control_closure_h100"

REPLAY_TARGETS = ("tp53", "brca2", "tsc2", "crebbp")
NEGATIVE_GUARDRAILS = ("BRCA1", "MSH2")

TP53_SEQUENCE = (
    "MEEPQSDPSVEPPLSQETFSDLWKLLPENNVLSPLPSQAMDDLMLSPDDIEQWFTEDPGP"
    "DEAPRMPEAAPPVAPAPAAPTPAAPAPAPSWPLSSSVPSQKTYQGSYGFRLGFLHSGTAK"
    "SVTCTYSPALNKMFCQLAKTCPVQLWVDSTPPPGTRVRAMAIYKQSQHMTEVVRRCPHHER"
    "CSDSDGLAPPQHLIRVEGNLRVEYLDDRNTFRHSVVVPYEPPEVGSDCTTIHYNYMCNSS"
    "CMGGMNRRPILTIITLEDSSGNLLGRNSFEVRVCACPGRDRRTEEENLRKKGEPHHELPP"
    "GSTKRALPNNTSSSPQPKKKPLDGEYFTLQIRGRERFEMFRELNEALELKDAQAGKEPGGS"
    "RAHSSHLKSKKGQSTSRHKKLMFKTEGPDSD"
)


def relative_to_project(path: Path) -> str:
    return path.resolve().relative_to(PROJECT_ROOT).as_posix()
