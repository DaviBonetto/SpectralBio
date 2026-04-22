from __future__ import annotations

from pathlib import Path

from spectralbio.replay import run_replay_target


def test_replay_targets_emit_required_bundle_files(tmp_path: Path) -> None:
    for target in ("tp53", "brca2", "tsc2", "crebbp"):
        target_dir = tmp_path / target
        result = run_replay_target(target, output_dir=target_dir)
        assert result["status"] == "PASS"
        for filename in (
            "summary.json",
            "verification.json",
            "provenance.json",
            "manifest.json",
            "metrics.json",
            "checksums.json",
            "status.json",
        ):
            assert (target_dir / filename).exists()
