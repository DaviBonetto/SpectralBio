"""Metric computation for the frozen benchmark artifacts."""

from __future__ import annotations

from typing import Any

from spectralbio.pipeline.combine_scores import combined_score, normalize


def _roc_auc_score(labels: list[int], scores: list[float]) -> float:
    paired = sorted((float(score), int(label)) for score, label in zip(scores, labels))
    positive = sum(labels)
    negative = len(labels) - positive
    if positive == 0 or negative == 0:
        raise ValueError("ROC AUC requires both positive and negative labels.")

    rank_sum = 0.0
    index = 0
    while index < len(paired):
        next_index = index + 1
        while next_index < len(paired) and paired[next_index][0] == paired[index][0]:
            next_index += 1
        average_rank = (index + 1 + next_index) / 2.0
        positives_in_tie = sum(label for _, label in paired[index:next_index])
        rank_sum += average_rank * positives_in_tie
        index = next_index

    return float((rank_sum - positive * (positive + 1) / 2.0) / (positive * negative))


def canonical_metrics(scores: list[dict[str, Any]]) -> dict[str, float]:
    labels = [int(row["label"]) for row in scores]
    frob = [float(row["frob_dist"]) for row in scores]
    ll = [float(row["ll_proper"]) for row in scores]
    frob_norm = normalize(frob)
    ll_norm = normalize(ll)
    combined = [combined_score(frob_value, ll_value) for frob_value, ll_value in zip(frob_norm, ll_norm)]
    combined_norm = normalize(combined)
    return {
        "auc_frob_dist": _roc_auc_score(labels, frob_norm),
        "auc_ll_proper": _roc_auc_score(labels, ll_norm),
        "auc_best_pair": _roc_auc_score(labels, combined_norm),
    }
