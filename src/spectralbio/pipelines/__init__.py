"""Replay and regeneration wrappers built on top of the legacy pipeline."""

from .brca2 import materialize_brca2_replay
from .crebbp import materialize_crebbp_replay
from .full_regeneration import materialize_full_reproduction_report
from .holdout_control import materialize_holdout_control_surface
from .portability import materialize_portability_surface
from .scale_repair import materialize_scale_repair_surface
from .tp53 import materialize_tp53_replay
from .tsc2 import materialize_tsc2_replay

__all__ = [
    "materialize_brca2_replay",
    "materialize_crebbp_replay",
    "materialize_full_reproduction_report",
    "materialize_holdout_control_surface",
    "materialize_portability_surface",
    "materialize_scale_repair_surface",
    "materialize_tp53_replay",
    "materialize_tsc2_replay",
]
