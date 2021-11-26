from itertools import permutations

from typing import List


class ChordSearch:
    def __init__(self, num_notes: int = 4):
        self.chords = _generate_chords(num_notes)


def _generate_chords(n):
    res = []
    perms = permutations(range(1, 12), n - 1)

    for perm in perms:
        res.append([0] + list(perm))

    return res


def pcs_to_asc(nums: List[int], start_note=0):
    """
    There's gotta be a better way to do this, but this works.
    """
    res = []
    last = None
    offset = 0
    for n in nums:
        if last:
            if n < last:
                offset += 12
            res.append(offset + n + start_note)
        else:
            res.append(n + start_note)

        last = n

    return res
