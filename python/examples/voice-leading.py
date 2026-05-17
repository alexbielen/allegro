from allegro.pitchclass import PitchClassSet
from allegro.voicing import voicings_from_pc_set, Voicing, DistanceMode

from itertools import permutations, pairwise




if __name__ == "__main__":
    mystic_chords = [0, 6, 10, 4, 9, 2]
    pcs = PitchClassSet(mystic_chords)

    five_note_subsets = []

    subsets = pcs.subsets(min_size=5)
    for subset in subsets:
        if len(subset.pitch_classes) == 5:
            five_note_subsets.append(subset)


    corpus = []

    for subset in five_note_subsets:
        voicings = voicings_from_pc_set(subset)
        for voicing in voicings:
            for i in range(12):
                transposed_voicing = [x + i for x in voicing.notes]

                # no minor nines
                if not 13 in voicing.all_intervals and not 25 in voicing.all_intervals:
                    corpus.append(Voicing(transposed_voicing))


    for voicing in corpus:
        distance = corpus[1].distance_to(voicing, DistanceMode.SumAbs)

        if voicing.notes[0] != corpus[0].notes[0] and distance < 6:
            pc = PitchClassSet([x % 12 for x in voicing.notes])
            pc2 = PitchClassSet([x % 12 for x in corpus[0].notes])
            print(f"{voicing.notes} to {corpus[0].notes} is {distance} -- {pc.prime_form} {pc.forte_num} -- {pc2.prime_form} {pc2.forte_num}") 
