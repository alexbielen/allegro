from allegro.numbers import (
    deltas,
    fit,
    FitMode,
)


def test_fit():
    assert fit(FitMode.WRAP, 1, 3, 2) == 2
    assert fit(FitMode.WRAP, 0, 6, 7) == 1
    assert fit(FitMode.WRAP, 0, 6, -1) == 5
    assert fit(FitMode.CLAMP, 1, 3, 2) == 2
    assert fit(FitMode.CLAMP, 1, 3, -1) == 1
    assert fit(FitMode.CLAMP, 1, 3, 4) == 3


def test_deltas():
    assert deltas([]) == []
    assert deltas([1]) == [1]
    assert deltas([3, 2, 1]) == [1, 1]
    assert deltas([5, 4, 3, 5, -1, -6]) == [1, 1, -2, 6, 5]
