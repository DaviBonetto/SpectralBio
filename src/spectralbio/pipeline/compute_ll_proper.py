"""LL Proper computation used by the thin Space client."""

from __future__ import annotations

import torch


def compute_ll_proper(
    logits_wt: torch.Tensor,
    local_pos: int,
    wt_aa: str,
    mut_aa: str,
    aa_token_ids: dict[str, int],
) -> float:
    token_index = local_pos + 1
    log_probs = torch.log_softmax(logits_wt[token_index], dim=-1)
    wt_id = aa_token_ids[wt_aa.upper()]
    mut_id = aa_token_ids[mut_aa.upper()]
    return float(log_probs[wt_id].item() - log_probs[mut_id].item())
