"""Small filesystem helpers used across the package."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from spectralbio.constants import PROJECT_ROOT


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> Path:
    ensure_dir(path.parent)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> Path:
    ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8")
    return path


def project_relpath(path: Path) -> str:
    return path.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix()


def read_tsv(path: Path) -> list[dict[str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines:
        return []

    headers = lines[0].split("\t")
    rows: list[dict[str, str]] = []
    for line in lines[1:]:
        values = line.split("\t")
        rows.append(dict(zip(headers, values)))
    return rows


def write_tsv(path: Path, rows: list[dict[str, Any]]) -> Path:
    ensure_dir(path.parent)
    if not rows:
        path.write_text("", encoding="utf-8")
        return path

    headers = list(rows[0].keys())
    lines = ["\t".join(headers)]
    for row in rows:
        lines.append("\t".join(str(row.get(header, "")) for header in headers))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
