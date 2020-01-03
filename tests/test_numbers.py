from allegro.numbers import fit, FitMode


def test_fit():
    assert fit(FitMode.WRAP, 1, 3, 2) == 2
    assert fit(FitMode.WRAP, 0, 6, 7) == 1
    assert fit(FitMode.WRAP, 0, 6, -1) == 5
    assert fit(FitMode.CLAMP, 1, 3, 2) == 2
    assert fit(FitMode.CLAMP, 1, 3, -1) == 1
    assert fit(FitMode.CLAMP, 1, 3, 4) == 3
