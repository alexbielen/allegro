from allegro.pitchclass import PitchClassSet
from itertools import permutations, pairwise

cantus_firmus = [76, 67, 72, 74, 70, 68]

allowed_harmonic_intervals = [3, 4, 7, 8, 9]
allowed_melodic_intervals = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]


if __name__ == "__main__":
    permutations_of_cantus_firmus = permutations(cantus_firmus, 6)
    all_permutations = []

    for permutation in permutations_of_cantus_firmus:
        for i in range(12):
            transposed_permutation = list(map(lambda x: x + -i, permutation))
            all_permutations.append(transposed_permutation)


    allowed_intervals_permutations = []

    # compare the intervals of the cantus firmus with the permutations
    # add to allowed_intervals_permutations if the intervals are in allowed_intervals
    def is_valid_melodic_solution(permutation):
        for x, y in pairwise(permutation):
            interval = y - x
            if interval not in allowed_melodic_intervals:
                return False
        return True

    def is_valid_harmonic_solution(permutation):
        for x, y in zip(cantus_firmus, permutation):
            interval = x - y
            if interval not in allowed_harmonic_intervals:
                return False
        return True

    for permutation in all_permutations:
        if is_valid_harmonic_solution(permutation):
            allowed_intervals_permutations.append(permutation)

    print(len(allowed_intervals_permutations))
    print(cantus_firmus)

    if allowed_intervals_permutations:
        cf_pcs = PitchClassSet([x % 12 for x in cantus_firmus])
        solution_pcs = PitchClassSet([x % 12 for x in allowed_intervals_permutations[0]])

        print(cf_pcs.forte_num())
        print(solution_pcs.forte_num())
    else:
        print("No valid solutions found")


    for permutation in allowed_intervals_permutations:
        intervals = []
        for x, y in zip(cantus_firmus, permutation):
            interval = x - y
            intervals.append(interval)
        
        print(f"Permutation: {permutation} - Intervals: {intervals}")


