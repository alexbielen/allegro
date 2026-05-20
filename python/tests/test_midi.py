import pytest

from allegro.midi import Pitch, keynum_to_pitch


class TestKeynumToPitch:
    def test_middle_c(self):
        pitch = keynum_to_pitch(60)
        assert isinstance(pitch, Pitch)
        assert pitch.keynum == 60
        assert pitch.name == "C4"

    def test_sharp(self):
        assert keynum_to_pitch(61).name == "C#4"

    def test_lower_octave(self):
        assert keynum_to_pitch(48).name == "C3"

    def test_midi_zero(self):
        assert keynum_to_pitch(0).name == "C-1"

    @pytest.mark.parametrize(
        ("keynum", "expected"),
        [
            (69, "A4"),
            (72, "C5"),
            (127, "G9"),
        ],
    )
    def test_common_notes(self, keynum, expected):
        assert keynum_to_pitch(keynum).name == expected
