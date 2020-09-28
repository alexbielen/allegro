import statistics
from typing import List
from collections import defaultdict

from allegro import midi
from allegro.cache import Cache
from allegro.constraints import Problem, unique_pitch_classes
from allegro.iterables import current_with_next
from music21.chord import Chord
import time


def katabasis(num_notes: int):
    p = Problem()
    lower_bound = 22
    upper_bound = 108

    notes = [p.add_constant(21)]
    for i in range(num_notes - 1):
        var = p.add_variable(lower_bound, upper_bound, f"n{i}")
        notes.append(var)

    intervals = []
    for i in range(num_notes - 1):
        var = p.add_variable(1, 7, f"i{i}")
        intervals.append(var)

    p.add_all_different_constraint(notes)

    # variables should ascend
    for i, (current, next_) in enumerate(current_with_next(notes)):
        if next_:
            p.add_constraint(current + intervals[i] == next_)

    num_intervals = num_notes - 1

    for i in range(num_intervals):
        if i == (num_intervals) // 2:  # floor division
            break
        p.add_constraint(intervals[i] == intervals[num_intervals - (i + 1)])

    p.add_filter(unique_pitch_classes)
    solutions = p.solve(for_variables=notes)
    return solutions


def categorize(chord: List[int]):
    chord = Chord(notes=chord)
    prime_form = chord.primeFormString
    interval_vector = chord.intervalVector
    forte = chord.forteClass
    stdev = statistics.stdev(interval_vector)
    return f"{prime_form} - {forte} - {interval_vector} - {stdev}"


def bucket_12(results):
    bucket = defaultdict(list)
    for result in results:
        category = categorize(result[0:6])
        bucket[category].append(result)

    return bucket


def bucket_7(results):
    bucket = defaultdict(list)
    for result in results:
        category = categorize(result)
        bucket[category].append(result)

    return bucket


def bucket_tetra_7(results):
    """
    Overlapping tetra chords
    """

    bucket = defaultdict(list)

    categorized = []
    for result in results:
        tetra1 = categorize(result[0:4])
        tetra2 = categorize(result[3:])

        bucket[tetra1].append(result)
        bucket[tetra2].append(result)

        categorized.append(
            {
                "category": categorize(result),
                "original": [note - 21 for note in result],
                "tetra1": categorize(result[0:4]),
                "tetra2": categorize(result[3:]),
            }
        )

    return bucket, categorized


def load_or_calculate(name: str, function):
    c = Cache()
    try:
        results = c.load(name)
    except IOError:
        results = function()
        c.save(results, name)

    return results


if __name__ == "__main__":

    ports = midi.get_output_ports()
    print(ports)
    m = midi.MidiOut(1)

    results_12_tone = load_or_calculate("12-tone-chords", lambda: katabasis(12))
    results_7_tone = load_or_calculate("7-tone-chords", lambda: katabasis(7))

    categorized_12 = load_or_calculate(
        "12-tone-prime-forms", lambda: bucket_12(results_12_tone)
    )

    categorized_7 = load_or_calculate(
        "7-tone-prime-forms", lambda: bucket_7(results_7_tone)
    )

    # print("\n Hexachords by category...")
    # for category, members in categorized_12.items():
    #     print(f"Category {category} has {len(members)} members.")

    # print("\n Septachords chords by category...")
    # for category, members in categorized_7.items():
    #     print(f"Category {category} has {len(members)} members.")

    bucket_tetra_7, tetra_seven = bucket_tetra_7(results_7_tone)

    for category, members in bucket_tetra_7.items():
        print(f"Category {category} has {len(members)} members.")

    for result in tetra_seven:
        if "4-15" in result["tetra1"] or "4-15" in result["tetra2"]:
            print(f"Playing {result}")
            transposed = [n + 48 for n in result["original"]]
            for note in transposed:
                m.play(note, 20, 0.2)

            time.sleep(3)

            m.play(transposed, 30, 5)

