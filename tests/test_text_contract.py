from __future__ import annotations

from spectralbio.constants import REQUIRED_TRANSFER_PHRASE
from spectralbio.pipeline.verify import verify_text_contract


def test_verify_text_contract_ignores_negated_forbidden_phrases(tmp_path) -> None:
    doc = tmp_path / "doc.md"
    doc.write_text(
        "\n".join(
                [
                    "- No `any protein` claim",
                    "- No `works on any protein` claim",
                    "- No strong, exceptional, or broad cross-protein generalization claim",
                    "- No clinical deployment or clinical use framing",
                    f"This repository reports {REQUIRED_TRANSFER_PHRASE}.",
                ]
            )
            + "\n",
        encoding="utf-8",
    )

    findings = verify_text_contract([doc])

    assert findings["forbidden_hits"] == []
    assert findings["required_phrase_present"] is True


def test_verify_text_contract_flags_active_forbidden_phrase(tmp_path) -> None:
    doc = tmp_path / "doc.md"
    doc.write_text(
        "\n".join(
                [
                    "This method works on any protein.",
                    f"This repository reports {REQUIRED_TRANSFER_PHRASE}.",
                ]
            )
            + "\n",
        encoding="utf-8",
    )

    findings = verify_text_contract([doc])

    assert set(findings["forbidden_hits"]) == {"works on any protein", "any protein"}
    assert findings["required_phrase_present"] is True
