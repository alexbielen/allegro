from allegro.search import _generate_chords, pcs_to_asc
from allegro.transform import deltas


def exhibits_symmetry(notes):
    if (
        notes[0] == notes[10]
        and notes[1] == notes[9]
        and notes[2] == notes[8]
        and notes[3] == notes[7]
        and notes[4] == notes[6]
    ):
        return True
    else:
        return False


if __name__ == "__main__":
    chords = _generate_chords(12)

    ascending = []
    final = []

    for chord in chords:
        ascending.append(pcs_to_asc(chord, 22))

    for chord in ascending:
        d = deltas(chord)
        if exhibits_symmetry(d):
            final.append(chord)

    print(final)
    print(len(final))
