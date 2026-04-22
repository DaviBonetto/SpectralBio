from __future__ import annotations

from pathlib import Path

from spectralbio.replay import run_replay_target
from spectralbio.utils.io import read_json


def test_tp53_replay_is_deterministic(tmp_path: Path) -> None:
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"
    run_replay_target("tp53", output_dir=first_dir)
    run_replay_target("tp53", output_dir=second_dir)

    first_summary = read_json(first_dir / "summary.json")
    second_summary = read_json(second_dir / "summary.json")
    first_checksums = read_json(first_dir / "checksums.json")
    second_checksums = read_json(second_dir / "checksums.json")

    assert first_summary["metrics"] == second_summary["metrics"]
    assert first_checksums["sha256"]["summary.json"] == second_checksums["sha256"]["summary.json"]
