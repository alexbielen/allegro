from more_itertools import pairwise

from allegro.constraints import Problem, unique_pitch_classes


def katabasis():
    p = Problem()

    num_notes = 12
    lower_bound = 22
    upper_bound = 108

    notes = [p.add_constant(22)]
    for i in range(num_notes - 1):
        var = p.add_variable(lower_bound, upper_bound, f"n{i}")
        notes.append(var)

    intervals = []
    for i in range(num_notes - 1):
        var = p.add_variable_from_domain([1, 2, 3, 4, 5, 7], f"i{i}")
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

    solutions = p.solve(for_variables=notes)
    return solutions


def list_to_midicents(l):
    return [x * 100 for x in l]


if __name__ == "__main__":
    res = [list_to_midicents(l) for l in katabasis()]
    print(res)

    # intervals present in Lulu row
    # 1 2 3 4 5 7
