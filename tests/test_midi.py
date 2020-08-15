from allegro.midi import keynum_to_notename


def test_keynum_to_notename():

    assert keynum_to_notename(21) == "A0"
    assert keynum_to_notename(60) == "C4"
    assert keynum_to_notename(59) == "B3"

    # test bounds
    assert keynum_to_notename(0) == "C-1"
    assert keynum_to_notename(127) == "G9"

