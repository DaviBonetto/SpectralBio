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
RELEASE_DIR = ARTIFACTS_DIR / "release" / "claw4s_2026"

TP53_CONFIG_PATH = PROJECT_ROOT / "configs" / "tp53_canonical.yaml"
BRCA1_TRANSFER_CONFIG_PATH = PROJECT_ROOT / "configs" / "brca1_transfer.yaml"
TP53_BENCHMARK_MANIFEST_PATH = BENCHMARKS_DIR / "manifests" / "tp53_canonical_manifest.json"
BRCA1_TRANSFER_MANIFEST_PATH = BENCHMARKS_DIR / "manifests" / "brca1_transfer_manifest.json"
CHECKSUMS_PATH = BENCHMARKS_DIR / "manifests" / "checksums.json"

MODEL_NAME = "facebook/esm2_t30_150M_UR50D"
SEED = 42
WINDOW_RADIUS = 40
ALPHA = 0.55

PRIMARY_CLAIM = "TP53 canonical executable benchmark"
SECONDARY_CLAIM = "bounded transfer on a fixed BRCA1 subset (N=100) without retraining"
ADAPTATION_CLAIM = "adaptation recipe only"

CANONICAL_COMMAND = "spectralbio canonical"
TRANSFER_COMMAND = "spectralbio transfer"
VERIFY_COMMAND = "spectralbio verify"
EXPORT_HF_SPACE_COMMAND = "spectralbio export-hf-space"
EXPORT_HF_DATASET_COMMAND = "spectralbio export-hf-dataset"
RELEASE_COMMAND = "spectralbio release"

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

EXPECTED_METRICS_PATH = ARTIFACTS_DIR / "expected" / "expected_metrics.json"
EXPECTED_FILES_PATH = ARTIFACTS_DIR / "expected" / "expected_files.json"
OUTPUT_SCHEMA_PATH = ARTIFACTS_DIR / "expected" / "output_schema.json"
VERIFICATION_RULES_PATH = ARTIFACTS_DIR / "expected" / "verification_rules.json"

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
