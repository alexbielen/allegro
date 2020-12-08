from more_itertools import pairwise

from allegro.constraints import Problem, unique_pitch_classes


def katabasis():
    p = Problem()

    num_notes = 12
    lower_bound = 22
    upper_bound = 108

    notes = [p.add_constant(21)]
    for i in range(num_notes - 1):
        var = p.add_variable(lower_bound, upper_bound, f"n{i}")
        notes.append(var)

    intervals = []
    for i in range(num_notes - 1):
        var = p.add_variable(1, 7, f"i{i}")
        intervals.append(var)

    p.add_all_different_constraint(notes)

    # variables should ascend
    for i, (current, next_) in enumerate(pairwise(notes)):
        p.add_constraint(current + intervals[i] == next_)

    p.add_constraint(intervals[0] == intervals[10])
    p.add_constraint(intervals[1] == intervals[9])
    p.add_constraint(intervals[2] == intervals[8])
    p.add_constraint(intervals[3] == intervals[7])
    p.add_constraint(intervals[4] == intervals[6])

    p.add_filter(unique_pitch_classes)

    solutions = p.solve(show_variables=notes)
    return solutions


if __name__ == "__main__":
    pass
