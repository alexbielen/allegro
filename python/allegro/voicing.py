"""Voicing namespace: permutations, intervals, voice-leading distance."""

from .allegro import (
    DistanceMode,
    VoiceLeading,
    Voicing,
    voicings_from_pc_set,
    voicings_from_pc_set_in_keynum_range,
    voicings_from_pc_set_within_span,
)

__all__ = [
    "DistanceMode",
    "VoiceLeading",
    "Voicing",
    "voicings_from_pc_set",
    "voicings_from_pc_set_in_keynum_range",
    "voicings_from_pc_set_within_span",
]
