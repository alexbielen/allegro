from allegro.numbers import (
    QuantizeMode,
    deltas,
    fit,
    FitMode,
    fit_clamp,
    fit_wrap,
    quantize,
)


def test_fit():
    assert fit(FitMode.WRAP, 1, 3, 2) == 2
    assert fit(FitMode.WRAP, 0, 6, 7) == 1
    assert fit(FitMode.WRAP, 0, 6, -1) == 5
    assert fit(FitMode.CLAMP, 1, 3, 2) == 2
    assert fit(FitMode.CLAMP, 1, 3, -1) == 1
    assert fit(FitMode.CLAMP, 1, 3, 4) == 3


def test_fit_wrap():
    assert fit_wrap(1, 3, 2) == 2
    assert fit_wrap(0, 6, 7) == 1


def test_fit_clamp():
    assert fit_clamp(1, 3, 2) == 2
    assert fit_clamp(1, 3, -1) == 1


def test_deltas():
    assert deltas([]) == []
    assert deltas([1]) == [1]
    assert deltas([3, 2, 1]) == [1, 1]
    assert deltas([5, 4, 3, 5, -1, -6]) == [1, 1, -2, 6, 5]


def test_quantize():
    assert quantize(QuantizeMode.MIDTREAD, 2, 13) == 14
