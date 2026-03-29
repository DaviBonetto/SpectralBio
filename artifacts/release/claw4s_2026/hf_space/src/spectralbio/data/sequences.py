"""Sequence loading helpers."""

from __future__ import annotations

from functools import lru_cache

from spectralbio.constants import BRCA1_SEQUENCE_PATH, TP53_SEQUENCE_PATH


def _parse_fasta(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "".join(line for line in lines if not line.startswith(">"))


@lru_cache(maxsize=2)
def load_tp53_sequence() -> str:
    return _parse_fasta(TP53_SEQUENCE_PATH.read_text(encoding="utf-8"))


@lru_cache(maxsize=2)
def load_brca1_sequence() -> str:
    return _parse_fasta(BRCA1_SEQUENCE_PATH.read_text(encoding="utf-8"))


def load_sequence_for_gene(gene: str) -> str:
    gene_upper = gene.upper()
    if gene_upper == "TP53":
        return load_tp53_sequence()
    if gene_upper == "BRCA1":
        return load_brca1_sequence()
    raise ValueError(f"Unsupported gene: {gene}")
