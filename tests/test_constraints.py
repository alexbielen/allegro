from allegro.constraints import unique_pitch_classes, Problem


def test_unique_pitch_classes():
    assert unique_pitch_classes([0, 1, 16, 17])
    assert not unique_pitch_classes([0, 12, 24])


def test_problem():
    problem = Problem()
    x = problem.add_variable(1, 2, "x")
    y = problem.add_variable(1, 2, "y")
    z = problem.add_variable(0, 3, "z")
    problem.add_constraint(x + y == z)
    solutions = problem.solve()

    assert solutions == [[1, 1, 2], [1, 2, 3], [2, 1, 3]]

