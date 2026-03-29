"""Covariance feature extraction used by the shared demo core."""

from __future__ import annotations

import numpy as np
from scipy.linalg import eigvalsh


def covariance_features(hidden_wt: np.ndarray, hidden_mut: np.ndarray) -> dict[str, float]:
    frob_dists: list[float] = []
    trace_ratios: list[float] = []
    shifts_log: list[float] = []

    for layer_index in range(hidden_wt.shape[0]):
        cov_wt = np.cov(hidden_wt[layer_index].T)
        cov_mut = np.cov(hidden_mut[layer_index].T)

        frob_dists.append(float(np.linalg.norm(cov_mut - cov_wt, "fro")))

        trace_wt = float(np.trace(cov_wt))
        trace_mut = float(np.trace(cov_mut))
        if abs(trace_wt) > 1e-12:
            trace_ratios.append(abs((trace_mut / trace_wt) - 1.0))
        else:
            trace_ratios.append(0.0)

        ev_wt = np.sort(np.abs(eigvalsh(cov_wt))) + 1e-12
        ev_mut = np.sort(np.abs(eigvalsh(cov_mut))) + 1e-12
        min_len = min(len(ev_wt), len(ev_mut))
        shifts_log.append(float(np.linalg.norm(np.log(ev_mut[:min_len]) - np.log(ev_wt[:min_len])) ** 2))

    return {
        "frob_dist": float(np.mean(frob_dists)),
        "trace_ratio": float(np.mean(trace_ratios)),
        "sps_log": float(np.mean(shifts_log)),
    }
