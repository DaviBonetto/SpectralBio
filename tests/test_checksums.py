from __future__ import annotations

from pathlib import Path

from spectralbio.checksums import verify_checksums
from spectralbio.replay import run_replay_target
from spectralbio.utils.io import read_json


def test_replay_checksums_validate(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "tp53"
    run_replay_target("tp53", output_dir=bundle_dir)
    payload = read_json(bundle_dir / "checksums.json")
    report = verify_checksums(payload["sha256"], bundle_dir)
    assert report["status"] == "PASS"
