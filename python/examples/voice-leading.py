from collections.abc import Callable, Iterable

from allegro.midi import keynum_to_pitch
from allegro.pitchclass import PitchClassSet, satisfy_pc
from allegro.voicing import DistanceMode, Voicing, voicings_from_pc_set_in_keynum_range

Rule = Callable[[Voicing], bool]


def transpose_voicing(voicing: Voicing, semitones: int) -> Voicing:
    return Voicing([note + semitones for note in voicing.notes])


def has_no_minor_nines(voicing: Voicing) -> bool:
    return 13 not in voicing.all_intervals and 25 not in voicing.all_intervals


def expand_voicings(
    pcs: PitchClassSet,
    min_keynum: int,
    max_keynum: int,
    rules: Iterable[Rule] = (),
    transpositions: Iterable[int] = (0,),
) -> list[Voicing]:
    base_voicings = voicings_from_pc_set_in_keynum_range(pcs, min_keynum, max_keynum)
    predicates = tuple(rules)

    result: list[Voicing] = []
    for voicing in base_voicings:
        for semitones in transpositions:
            candidate = transpose_voicing(voicing, semitones)
            if all(rule(candidate) for rule in predicates):
                result.append(candidate)
    return result


def subset_voicings(
    pcs: PitchClassSet,
    subset_size: int,
    min_keynum: int,
    max_keynum: int,
    rules: Iterable[Rule] = (),
    transpositions: Iterable[int] = (0,),
) -> list[Voicing]:
    corpus: list[Voicing] = []
    for subset in pcs.subsets(min_size=subset_size):
        if len(subset.pitch_classes) == subset_size:
            corpus.extend(
                expand_voicings(
                    subset,
                    min_keynum,
                    max_keynum,
                    rules=rules,
                    transpositions=transpositions,
                )
            )
    return corpus


def delta_notes(starting_voicing: Voicing, other_voicing: Voicing) -> list[int]:
    return [note for note in other_voicing.notes if note not in starting_voicing.notes]


def print_close_voicings(
    corpus: Iterable[Voicing],
    starting_voicing: Voicing,
    max_distance: int = 4,
) -> None:
    sv_set = PitchClassSet([note % 12 for note in starting_voicing.notes])
    starting_pitch_names = [keynum_to_pitch(note).name for note in starting_voicing.notes]
    print("=" * 72)
    print("Close voicings")
    print(f"start: {' '.join(starting_pitch_names)}")
    print(f"set:   {sv_set.forte_num}")
    print(f"max distance: {max_distance}")
    print("=" * 72)

    for voicing in corpus:
        distance = starting_voicing.distance_to(voicing, DistanceMode.SumAbs)
        if voicing.notes[0] == starting_voicing.notes[0] or distance > max_distance:
            continue

        voicing_pc_set = PitchClassSet([note % 12 for note in voicing.notes])
        pitch_names = [keynum_to_pitch(note).name for note in voicing.notes]
        diffs = delta_notes(starting_voicing, voicing)
        diffs_set = PitchClassSet([note % 12 for note in diffs])
        print(f"notes: {' '.join(pitch_names)}")
        print(f"midi:  {voicing.notes}")
        print(f"set:   {voicing_pc_set.forte_num}")
        print(f"dist:  {distance}")
        print(
            f"diff:  {diffs} | {diffs_set.forte_num} | "
            f"iv={diffs_set.interval_vector}"
        )
        print(f"satis: {satisfy_pc('7-23A', [note % 12 for note in voicing.notes])}")
        print("-" * 72)


if __name__ == "__main__":
    # mystic_pcs = PitchClassSet([0, 6, 10, 4, 9, 2])
    rules = [has_no_minor_nines]
    pcs = PitchClassSet([0,2,3,4,5,7,9])
    corpus = subset_voicings(
        pcs=pcs,
        subset_size=6,
        min_keynum=36,
        max_keynum=100,
        rules=rules,
        transpositions=range(12),  # transpose all generated voicings by 0..11
    )


    # corpus = expand_voicings(
    #     pcs,
    #     min_keynum=36,
    #     max_keynum=100,
    #     rules=[has_no_minor_nines],
    #     transpositions=range(12),
    # )

    nice_voicing = Voicing([62, 66, 68, 73, 76, 83])
    print_close_voicings(corpus, nice_voicing, max_distance=4)



