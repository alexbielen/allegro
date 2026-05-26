from allegro.pitchclass import PitchClassSet
from allegro.voicing import voicings_from_pc_set_in_keynum_range, Voicing, DistanceMode
from allegro.midi import keynum_to_pitch
from itertools import permutations, pairwise




if __name__ == "__main__":
    mystic_chords = [0, 6, 10, 4, 9, 2]
    pcs = PitchClassSet(mystic_chords)

    mystic_five_note_subsets = []

    subsets = pcs.subsets(min_size=5)
    for subset in subsets:
        if len(subset.pitch_classes) == 5:
            mystic_five_note_subsets.append(subset)

    

    corpus = []

    for subset in mystic_five_note_subsets:
        voicings = voicings_from_pc_set_in_keynum_range(subset, 34, 86)
        for voicing in voicings:
            for i in range(12):
                transposed_voicing = [x + i for x in voicing.notes]

                # no minor nines
                if not 13 in voicing.all_intervals and not 25 in voicing.all_intervals:
                    corpus.append(Voicing(transposed_voicing))


    def delta_intervals(starting_voicing, voicing):
        differences = []

        for x in voicing.notes:
            if x not in starting_voicing.notes:
                differences.append(x)

        return differences







    def distance_to_starting_voicing(starting_voicing):
        sv_set = PitchClassSet([x % 12 for x in starting_voicing.notes])
        starting_pitch_names = [keynum_to_pitch(x).name for x in starting_voicing.notes]
        print(f"starting voicing: {starting_pitch_names} is {sv_set.forte_num}")
        for voicing in corpus:
            distance = starting_voicing.distance_to(voicing, DistanceMode.SumAbs)


            if voicing.notes[0] != starting_voicing.notes[0] and distance < 5:
                pc = PitchClassSet([x % 12 for x in voicing.notes])
                pitch_names = [keynum_to_pitch(x).name for x in voicing.notes]
                diffs = delta_intervals(starting_voicing, voicing)
                diffs_set = PitchClassSet([x % 12 for x in diffs])
                print(f"{pitch_names} is {pc.forte_num} -- distance {distance} -- diff: {diffs} -- {diffs_set.forte_num}, {diffs_set.interval_vector}")
                print(f"{voicing.notes}")




    nice_voicing = Voicing([57, 64, 72, 74, 78])
    harmonic_series_like = Voicing([48, 67, 76, 82, 86])

    distance_to_starting_voicing(nice_voicing)



