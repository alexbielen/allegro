from allegro.numbers import fit, FitMode


def test_fit_wrap():
    assert fit(1, 0, 10, FitMode.Wrap) == 1
    assert fit(10, 0, 10, FitMode.Wrap) == 10
    assert fit(12, 0, 10, FitMode.Wrap) == 2
    assert fit(25, 0, 10, FitMode.Wrap) == 5
    assert fit(-4, 0, 10, FitMode.Wrap) == 6
    assert fit(-16, 0, 10, FitMode.Wrap) == 4
    assert fit(-53, 0, 10, FitMode.Wrap) == 7


def test_fit_reflect():
    assert fit(12, 0, 10, FitMode.Reflect) == 8
    assert fit(-4, 0, 10, FitMode.Reflect) == 4


def test_fit_clamp():
    assert fit(12, 0, 10, FitMode.Clamp) == 10
    assert fit(-4, 0, 10, FitMode.Clamp) == 0
