# Voices

This part of the application will deal with voice-leading between chords.

A voicing is a specific arrangement of pitches.

Let's look at a C major chord.

First, we can permute the [0, 4, 7] pitch class set all ways. And then
we will arrange the notes using Midi Keynums where C = 60.

[0, 4, 7] -> [60, 64, 67]
[0, 7, 4] -> [60, 67, 76]
[4, 0, 7] -> [52, 60, 67]
[4, 7, 0] -> [52, 55, 60]
[7, 0, 4] -> [55, 60, 64]
[7, 4, 0] -> [43, 52, 60]

This creates unique interval patterns:

[60, 64, 67] has the intervals [3, 4, 7] (from largest to smallest) or between notes [4, 3]
[60, 67, 76] has the intervals [7, 9, 16] or between notes [7, 9]
[52, 60, 67] has the intervals [8, 7, 15] or between notes [8, 7]
[52, 55, 60] has the intervals [3, 5, 8] or between notes [3, 5]
[55, 60, 64] has the intervals [4, 5, 9] or between notes [5, 4]
[43, 52, 60] has the intervals [8, 9, 17] or between notes [9, 8]

We can look at another type of chord, an A minor chord [9, 0, 4] again with C (0) at 60.

[9, 0, 4] -> [57, 60, 64]
[9, 4, 0] -> [45, 52, 60]
[0, 9, 4] -> [60, 69, 76]
[0, 4, 9] -> [60, 64, 69]
[4, 9, 0] -> [52, 57, 60]
[4, 0, 9] -> [52, 60, 69]

Now, we can compare the distance between voicings. For example:

[60, 64, 67] compared with [57, 60, 64] in absolute difference gives [3, 4, 3] which sums to 10.

[57, 60, 64] compared with [55, 60, 64] in absolute different gives [2, 0, 0] which sums to 2.

So, we could say that the second of the two ([57, 60, 64] -> [55, 60, 64]) move to each other more "efficiently" or elegantly or parsimoniously.

On the python side, we'll have a classes and an API roughly like this:

```
from allegro.voicing voicings_from_pc_set, VoiceLeading
from allegro.pitchclass import PitchClassSet


c_major = PitchClassSet([0, 4, 7])

# C4 = 60, B3 = 59, C#4 = 61 etc
c_major_voicings = voicings_from_pc_set(c_major, anchor='C4')

a_minor_voicing = Voicing([60, 64, 69])
a_minor_voicing2 = Voicing([57, 60, 64])

for voicing in a_minor_voicings:
    print(voicing.voicing) # [60, 64, 67]
    print(voicing.all_intervals) # [3, 4, 7] -- sorted
    print(voicing.adjacent_intervals) # [4, 3]
    print(voicing.span) # 7
    print(voicing.distance_to(a_minor_voicing, mode=SumAbs)) # 2
    print(voicing.distance_to(a_minor_voicing2, mode=SumAbs)) # 10

```

Let's write this API in Rust using structs and impl blocks.
