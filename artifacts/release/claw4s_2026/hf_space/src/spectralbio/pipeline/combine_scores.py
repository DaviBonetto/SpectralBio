"""Score-combination helpers shared by CLI and demo."""

from __future__ import annotations

from spectralbio.constants import ALPHA


def combined_score(frob_dist: float, ll_proper: float, alpha: float = ALPHA) -> float:
    return alpha * float(frob_dist) + (1.0 - alpha) * float(ll_proper)


def normalize(values: list[float]) -> list[float]:
    vector = [float(value) for value in values]
    if not vector:
        return []
    minimum = min(vector)
    maximum = max(vector)
    if maximum == minimum:
        return [0.0 for _ in vector]
    return [(value - minimum) / (maximum - minimum) for value in vector]
