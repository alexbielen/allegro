import allegro


def test_fit_wrap():
    assert allegro.fit(1, 0, 10, allegro.FitMode.Wrap) == 1
    assert allegro.fit(10, 0, 10, allegro.FitMode.Wrap) == 10
    assert allegro.fit(12, 0, 10, allegro.FitMode.Wrap) == 2
    assert allegro.fit(25, 0, 10, allegro.FitMode.Wrap) == 5
    assert allegro.fit(-4, 0, 10, allegro.FitMode.Wrap) == 6
    assert allegro.fit(-16, 0, 10, allegro.FitMode.Wrap) == 4
    assert allegro.fit(-53, 0, 10, allegro.FitMode.Wrap) == 7


def test_fit_reflect():
    assert allegro.fit(12, 0, 10, allegro.FitMode.Reflect) == 8
    assert allegro.fit(-4, 0, 10, allegro.FitMode.Reflect) == 4


def test_fit_clamp():
    assert allegro.fit(12, 0, 10, allegro.FitMode.Clamp) == 10
    assert allegro.fit(-4, 0, 10, allegro.FitMode.Clamp) == 0
