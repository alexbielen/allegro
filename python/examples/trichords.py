from allegro.pitchclass import PitchClassSet, transpose_ordered_set, invert_ordered_set
from itertools import combinations


def find_aggregate_covering_four(
    transpositions: list[list[int]],
) -> tuple[list[list[int]], PitchClassSet] | None:

    solutions = []

    for four_transpositions in combinations(transpositions, 4):
        combined = []
        for transposition in four_transpositions:
            combined.extend(transposition)

        unique_pitch_classes = sorted(set(combined))
        if len(unique_pitch_classes) == 12:
            solutions.append(list(four_transpositions))

    return solutions



if __name__ == "__main__":


    trichord = [4, 3, 0]
    all_transpositions_and_inversions = []

    for i in range(12):
        transposed_trichord = transpose_ordered_set(i, trichord)
        all_transpositions_and_inversions.append(transposed_trichord)
        all_transpositions_and_inversions.append(invert_ordered_set(transposed_trichord))


    solutions = find_aggregate_covering_four(all_transpositions_and_inversions)

    if solutions is None:
        print("No solutions found.")
    else:
        for solution in solutions:
            print(solution)
