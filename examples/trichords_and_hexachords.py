import itertools
from dataclasses import dataclass

from typing import List, Union

from music21 import chord


@dataclass
class TrichordData:
    notes: List[Union[int, str]]
    prime_form: str
    complement: List[Union[int, str]]
    complement_prime_form: str

    def pretty_print(self):
        print(
            f"""
Notes: {self.notes}
Prime Form: {self.prime_form}
Complement: {self.complement}
Complement Prime Form: {self.complement_prime_form}
              """
        )


def main():
    pass


def list_difference(main_set, subset):
    diff = [x for x in main_set if x not in subset]
    return diff


def get_trichords_in_hexachord(hexachord):
    hexachord_trichord_combos = itertools.combinations(hexachord, 3)
    res = []

    for combo in hexachord_trichord_combos:
        c = chord.Chord(combo)
        complement = list_difference(hexachord, combo)
        complement_chord = chord.Chord(complement)

        trichord = TrichordData(
            notes=combo,
            prime_form=c.primeFormString,
            complement=complement,
            complement_prime_form=complement_chord.primeFormString,
        )
        res.append(trichord)

    return res


if __name__ == "__main__":
    main()

    row_hexachord = ["D", "Bb", "F#", "G", "B", "Eb"]

    row_hexachord_trichords: List[TrichordData] = get_trichords_in_hexachord(
        row_hexachord
    )

    for trichord in row_hexachord_trichords:
        trichord.pretty_print()

    # mystic_chord_notes = ["C", "F#", "Bb", "E", "A", "D"]
    # # source_set_5_notes = [0, 1, 4, 5, 8, 9]
    # source_set_5_notes = [2, 3, 6, 7, 10, 11]

    # source_set_5_trichords: List[TrichordData] = get_trichords_in_hexachord(
    #     source_set_5_notes
    # )
    # mystic_trichords: List[TrichordData] = get_trichords_in_hexachord(
    #     mystic_chord_notes
    # )

    # ss_5_prime_forms = set()
    # mystic_prime_forms = set()

    # for trichord in source_set_5_trichords:
    #     ss_5_prime_forms.add(trichord.prime_form)
    #     ss_5_prime_forms.add(trichord.complement_prime_form)

    # for trichord in mystic_trichords:
    #     mystic_prime_forms.add(trichord.prime_form)
    #     mystic_prime_forms.add(trichord.complement_prime_form)

    # print(mystic_prime_forms)

    # for trichord in mystic_trichords:
    #     trichord.pretty_print()

    # print(ss_5_prime_forms)

    # for trichord in source_set_5_trichords:
    # trichord.pretty_print()
