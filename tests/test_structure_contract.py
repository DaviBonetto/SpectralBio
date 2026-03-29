from __future__ import annotations

from pathlib import Path

from spectralbio.cli import release_bundle
from spectralbio.configs import load_yaml


def test_src_layout_is_the_only_public_package_root() -> None:
    assert not Path("spectralbio").exists()
    assert not Path("sitecustomize.py").exists()
    package_init = Path("src/spectralbio/__init__.py").read_text(encoding="utf-8")
    assert "PROJECT_ROOT" in package_init


def test_huggingface_folder_is_compatibility_only() -> None:
    entries = {path.name for path in Path("huggingface").iterdir()}
    assert entries == {"README.md", "app.py", "dataset_card.md", "requirements.txt"}


def test_legacy_boundary_is_explicit_and_complete() -> None:
    for relative_path in (
        "legacy/README.md",
        "legacy/colab/spectralbio.ipynb",
        "legacy/colab_results/summary.json",
        "legacy/huggingface_assets/hero_bg.png.png",
        "legacy/huggingface_data/summary.json",
        "legacy/submit/submit.py",
    ):
        assert Path(relative_path).exists()


def test_public_assets_and_paper_surfaces_are_present() -> None:
    for relative_path in (
        "assets/branding/claw_lobster.png",
        "assets/generated/tp53_results_overview.png",
        "paper/spectralbio.tex",
        "publish/clawrxiv/spectralbio_clawrxiv.md",
    ):
        assert Path(relative_path).exists()


def test_publish_surfaces_are_complete() -> None:
    for relative_path in (
        "publish/hf_space/app.py",
        "publish/hf_space/README.md",
        "publish/hf_space/requirements.txt",
        "publish/hf_dataset/README.md",
        "publish/hf_dataset/dataset_manifest.json",
        "publish/clawrxiv/README.md",
    ):
        assert Path(relative_path).exists()


def test_release_dataset_mirror_matches_publish_surface() -> None:
    assert (
        Path("artifacts/release/claw4s_2026/hf_dataset/README.md").read_text(encoding="utf-8")
        == Path("publish/hf_dataset/README.md").read_text(encoding="utf-8")
    )
    assert (
        Path("artifacts/release/claw4s_2026/hf_dataset/dataset_manifest.json").read_text(encoding="utf-8")
        == Path("publish/hf_dataset/dataset_manifest.json").read_text(encoding="utf-8")
    )


def test_release_bundle_support_files_are_staged() -> None:
    release_bundle()
    for relative_path in (
        "artifacts/release/claw4s_2026/README.md",
        "artifacts/release/claw4s_2026/SKILL.md",
        "artifacts/release/claw4s_2026/docs/truth_contract.md",
        "artifacts/release/claw4s_2026/docs/reproducibility.md",
        "artifacts/release/claw4s_2026/benchmarks/manifests/checksums.json",
    ):
        assert Path(relative_path).exists()


def test_configs_target_canonical_outputs() -> None:
    tp53_config = load_yaml(Path("configs/tp53_canonical.yaml"))
    brca1_config = load_yaml(Path("configs/brca1_transfer.yaml"))

    assert tp53_config["output_dir"] == "outputs/canonical"
    assert brca1_config["output_dir"] == "outputs/transfer"


def test_obsolete_active_conflict_paths_are_absent() -> None:
    assert not Path("submit").exists()
    assert not Path("colab").exists()
    assert not Path("huggingface/data").exists()
    assert not Path("huggingface/assets").exists()
