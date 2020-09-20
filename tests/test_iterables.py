from allegro.iterables import current_with_next


def test_current_with_next():
    assert list(current_with_next([1, 2, 3])) == [(1, 2), (2, 3), (3, None)]
