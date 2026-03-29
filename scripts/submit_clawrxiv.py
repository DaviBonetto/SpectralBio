"""Submit the SpectralBio paper bundle to clawRxiv using environment-only credentials.

Security rules:
- never commit credentials
- read the secret from `CLAWRXIV_API_KEY` or an ignored local wrapper only
- never send the credential to any domain or IP other than `http://18.118.210.52`
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API_URL = "http://18.118.210.52/api/posts"


def _load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def build_payload() -> dict[str, object]:
    summary = json.loads(_load_text(ROOT / "artifacts" / "expected" / "expected_metrics.json"))
    return {
        "title": "SpectralBio: TP53 Canonical Benchmark with Bounded BRCA1 Transfer Evidence",
        "abstract": (
            "SpectralBio is a deterministic executable science artifact centered on a TP53 reproducibility benchmark "
            "with bounded BRCA1 transfer evidence on a fixed 100-variant subset without retraining."
        ),
        "content": _load_text(ROOT / "publish" / "clawrxiv" / "spectralbio_clawrxiv.md"),
        "tags": ["bioinformatics", "protein-language-models", "variant-effect-prediction", "claw4s-2026"],
        "human_names": ["Davi Bonetto"],
        "skill_md": _load_text(ROOT / "SKILL.md"),
        "metadata": summary,
    }


def main() -> int:
    api_key = os.environ.get("CLAWRXIV_API_KEY", "").strip()
    if not api_key:
        print("Missing CLAWRXIV_API_KEY environment variable.")
        return 1

    payload = json.dumps(build_payload()).encode("utf-8")
    request = urllib.request.Request(
        API_URL,
        data=payload,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            print(response.read().decode("utf-8"))
        return 0
    except urllib.error.HTTPError as exc:
        print(exc.read().decode("utf-8"))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
