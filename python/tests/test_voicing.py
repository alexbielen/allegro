from math import factorial

import pytest

from allegro.pitchclass import PitchClassSet
from allegro.voicing import (
    DistanceMode,
    Voicing,
    voicings_from_pc_set,
    voicings_from_pc_set_in_keynum_range,
    voicings_from_pc_set_within_span,
)


def _voicing_map(pcs, octave=4):
    """Map permutation tuple -> MIDI notes."""
    voicings = voicings_from_pc_set(pcs, octave=octave)
    out = {}
    for v in voicings:
        # Recover permutation order from pitch classes mod 12
        perm = tuple(n % 12 for n in v.notes)
        out[perm] = v.notes
    return out


class TestCMajorVoicings:
    C_MAJOR_EXPECTED = {
        (0, 4, 7): [60, 64, 67],
        (0, 7, 4): [60, 67, 76],
        (4, 0, 7): [52, 60, 67],
        (4, 7, 0): [52, 55, 60],
        (7, 0, 4): [55, 60, 64],
        (7, 4, 0): [43, 52, 60],
    }

    def test_all_six_permutations(self):
        pcs = PitchClassSet([0, 4, 7])
        got = _voicing_map(pcs)
        assert got == self.C_MAJOR_EXPECTED

    def test_count_is_factorial(self):
        pcs = PitchClassSet([0, 4, 7])
        voicings = voicings_from_pc_set(pcs)
        assert len(voicings) == factorial(3)


class TestAMinorVoicings:
    A_MINOR_EXPECTED = {
        (9, 0, 4): [57, 60, 64],
        (9, 4, 0): [45, 52, 60],
        (0, 9, 4): [60, 69, 76],
        (0, 4, 9): [60, 64, 69],
        (4, 9, 0): [52, 57, 60],
        (4, 0, 9): [52, 60, 69],
    }

    def test_all_six_permutations(self):
        # 0 first so anchor is C at 60 (spec register)
        pcs = PitchClassSet([0, 9, 4])
        got = _voicing_map(pcs)
        assert got == self.A_MINOR_EXPECTED


class TestVoicingMetrics:
    def test_intervals_and_span(self):
        v = Voicing([60, 64, 67])
        assert v.all_intervals == [3, 4, 7]
        assert v.adjacent_intervals == [4, 3]
        assert v.span == 7

    def test_distance_sum_abs(self):
        a = Voicing([60, 64, 67])
        b = Voicing([57, 60, 64])
        c = Voicing([55, 60, 64])
        assert a.distance_to(b, mode=DistanceMode.SumAbs) == 10
        assert b.distance_to(c, mode=DistanceMode.SumAbs) == 2


class TestErrors:
    def test_empty_pitch_class_set(self):
        pcs = PitchClassSet([])
        with pytest.raises(ValueError, match="must not be empty"):
            voicings_from_pc_set(pcs)

    def test_distance_length_mismatch(self):
        a = Voicing([60, 64, 67])
        b = Voicing([60, 64])
        with pytest.raises(ValueError, match="same number of voices"):
            a.distance_to(b)


class TestKeynumRange:
    def test_all_notes_in_range(self):
        pcs = PitchClassSet([0, 4, 7])
        voicings = voicings_from_pc_set_in_keynum_range(pcs, 36, 69)
        assert len(voicings) > 0
        for v in voicings:
            assert all(36 <= n <= 69 for n in v.notes)

    def test_includes_example_voicings(self):
        pcs = PitchClassSet([0, 4, 7])
        got = {tuple(v.notes) for v in voicings_from_pc_set_in_keynum_range(pcs, 36, 69)}
        assert (36, 52, 67) in got
        assert (40, 55, 60) in got
        assert (43, 48, 64) in got

    def test_includes_close_position(self):
        pcs = PitchClassSet([0, 4, 7])
        voicings = voicings_from_pc_set_in_keynum_range(pcs, 60, 72)
        assert [60, 64, 67] in [v.notes for v in voicings]

    def test_tighter_range_fewer_voicings(self):
        pcs = PitchClassSet([0, 4, 7])
        wide = voicings_from_pc_set_in_keynum_range(pcs, 36, 69)
        narrow = voicings_from_pc_set_in_keynum_range(pcs, 60, 67)
        assert len(narrow) < len(wide)

    def test_more_voicings_than_anchor_mode(self):
        pcs = PitchClassSet([0, 4, 7])
        anchored = voicings_from_pc_set(pcs)
        in_range = voicings_from_pc_set_in_keynum_range(pcs, 36, 69)
        assert len(in_range) > len(anchored)

    def test_invalid_range(self):
        pcs = PitchClassSet([0, 4, 7])
        with pytest.raises(ValueError, match="min_keynum"):
            voicings_from_pc_set_in_keynum_range(pcs, 72, 60)


class TestWithinSpan:
    def test_filters_by_span(self):
        pcs = PitchClassSet([0, 4, 7])
        voicings = voicings_from_pc_set_within_span(pcs, 7)
        assert len(voicings) > 0
        for v in voicings:
            assert v.span <= 7
        assert [60, 64, 67] in [v.notes for v in voicings]

    def test_excludes_wide_voicing(self):
        pcs = PitchClassSet([0, 4, 7])
        voicings = voicings_from_pc_set_within_span(pcs, 7)
        assert [36, 52, 67] not in [v.notes for v in voicings]

    def test_invalid_max_span(self):
        pcs = PitchClassSet([0, 4, 7])
        with pytest.raises(ValueError, match="max_span"):
            voicings_from_pc_set_within_span(pcs, -1)


class TestFirstPcAnchor:
    def test_exotic_set_anchor_midi(self):
        pcs = PitchClassSet([11, 3, 4, 7])
        voicings = voicings_from_pc_set(pcs, octave=4)
        # anchor pc 11 at B4 = 71 appears in every voicing
        for v in voicings:
            assert 71 in v.notes
        assert len(voicings) == factorial(4)

    def test_ordering_changes_register(self):
        low = voicings_from_pc_set(PitchClassSet([0, 9, 4]), octave=4)[0]
        high = voicings_from_pc_set(PitchClassSet([9, 0, 4]), octave=4)[0]
        assert low.notes != high.notes
