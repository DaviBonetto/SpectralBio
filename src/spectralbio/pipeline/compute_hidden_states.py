"""Hidden-state extraction for TP53 and BRCA1 local-window scoring."""

from __future__ import annotations

from functools import lru_cache

import torch
from transformers import EsmForMaskedLM, EsmTokenizer

from spectralbio.constants import MODEL_NAME, WINDOW_RADIUS
from spectralbio.utils.determinism import seed_all


@lru_cache(maxsize=1)
def model_bundle() -> tuple[EsmTokenizer, EsmForMaskedLM, str, dict[str, int]]:
    seed_all(42)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tokenizer = EsmTokenizer.from_pretrained(MODEL_NAME)
    model = EsmForMaskedLM.from_pretrained(MODEL_NAME).to(device).eval()
    aa_list = list("ACDEFGHIKLMNPQRSTVWY")
    aa_token_ids = {aa: tokenizer.convert_tokens_to_ids(aa) for aa in aa_list}
    return tokenizer, model, device, aa_token_ids


def extract_local_hidden_states(sequence: str, center_pos: int, window_radius: int = WINDOW_RADIUS):
    tokenizer, model, device, _ = model_bundle()
    start = max(0, center_pos - window_radius)
    end = min(len(sequence), center_pos + window_radius + 1)
    local_sequence = sequence[start:end]
    local_pos = center_pos - start

    inputs = tokenizer(local_sequence, return_tensors="pt", add_special_tokens=True, padding=False)
    inputs = {key: value.to(device) for key, value in inputs.items()}
    with torch.no_grad():
        outputs = model(**inputs, output_hidden_states=True)

    hidden = torch.stack(outputs.hidden_states[1:], dim=0)[:, 0, 1:-1, :].cpu().numpy()
    logits = outputs.logits[0].cpu()
    return hidden, logits, local_pos
