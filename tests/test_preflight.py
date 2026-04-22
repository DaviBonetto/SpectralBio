from __future__ import annotations

from pathlib import Path

import json

from spectralbio.preflight import run_doctor, run_preflight
from spectralbio.cli import main
from spectralbio.constants import STATUS_OUTPUT_DIR


def test_preflight_passes_for_repo_state(tmp_path: Path) -> None:
    report = run_preflight(
        cache_dir=tmp_path / "cache",
        output_dir=tmp_path / "replay",
        offline=True,
        cpu_only=True,
    )
    assert report["status"] == "PASS"
    assert report["checks"]["schema_files_present"] is True
    assert report["checks"]["replay_assets_present"] is True


def test_doctor_returns_structured_diagnosis(tmp_path: Path) -> None:
    report = run_doctor(
        cache_dir=tmp_path / "cache",
        output_dir=tmp_path / "replay",
        offline=True,
        cpu_only=True,
    )
    assert report["status"] == "PASS"
    assert report["category"] == "healthy"


def test_doctor_command_writes_diagnosis_bundle(tmp_path: Path) -> None:
    exit_code = main(
        [
            "doctor",
            "--json",
            "--cpu-only",
            "--offline",
            "--output-dir",
            str(tmp_path / "replay"),
            "--cache-dir",
            str(tmp_path / "cache"),
        ]
    )
    assert exit_code == 0
    assert (STATUS_OUTPUT_DIR / "latest" / "diagnosis.json").exists()


def test_non_doctor_command_clears_stale_latest_diagnosis(tmp_path: Path, capsys) -> None:
    doctor_exit = main(
        [
            "doctor",
            "--json",
            "--cpu-only",
            "--offline",
            "--output-dir",
            str(tmp_path / "replay"),
            "--cache-dir",
            str(tmp_path / "cache"),
        ]
    )
    capsys.readouterr()
    assert doctor_exit == 0
    assert (STATUS_OUTPUT_DIR / "latest" / "diagnosis.json").exists()

    preflight_exit = main(
        [
            "preflight",
            "--json",
            "--cpu-only",
            "--offline",
            "--output-dir",
            str(tmp_path / "replay"),
            "--cache-dir",
            str(tmp_path / "cache"),
        ]
    )
    capsys.readouterr()
    assert preflight_exit == 0
    assert not (STATUS_OUTPUT_DIR / "latest" / "diagnosis.json").exists()


def test_explain_status_uses_global_surface_label_when_target_is_null(capsys) -> None:
    payload = {
        "command": "spectralbio reproduce-all --json --cpu-only --offline",
        "status": "PASS",
        "exit_code": 0,
        "mode": "reproduce-all",
        "target": None,
        "surface_role": "reproduce-all",
        "started_at": "2026-04-22T00:00:00+00:00",
        "finished_at": "2026-04-22T00:00:01+00:00",
        "duration_seconds": 1.0,
        "offline": True,
        "cpu_only": True,
        "artifacts_used": [],
        "artifacts_emitted": [],
        "checks_performed": [],
        "metrics": {},
        "warnings": [],
        "next_action": "none",
        "details": {"command": "reproduce-all"},
    }
    (STATUS_OUTPUT_DIR / "latest").mkdir(parents=True, exist_ok=True)
    (STATUS_OUTPUT_DIR / "latest" / "status.json").write_text(json.dumps(payload), encoding="utf-8")
    diagnosis = STATUS_OUTPUT_DIR / "latest" / "diagnosis.json"
    if diagnosis.exists():
        diagnosis.unlink()

    exit_code = main(
        [
            "explain-status",
            "--path",
            str(STATUS_OUTPUT_DIR / "latest" / "status.json"),
            "--json",
            "--cpu-only",
            "--offline",
        ]
    )
    output = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert "for global surface" in output["explanation"]
