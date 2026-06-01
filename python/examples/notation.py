"""Build grand-staff MNX chord charts from MIDI key numbers."""

from __future__ import annotations

from pathlib import Path

from allegro.midi import keynum_to_pitch
from allegro.mnx import (
    BarlineType,
    ClefSign,
    MnxBarline,
    MnxClef,
    MnxDocument,
    MnxEvent,
    MnxGlobalData,
    MnxKeySignature,
    MnxMeasureGlobal,
    MnxMetadata,
    MnxNote,
    MnxNoteValue,
    MnxPart,
    MnxPartMeasure,
    MnxPitch,
    MnxPositionedClef,
    MnxSequence,
    MnxTimeSignature,
    NoteStep,
    NoteValueBase,
)

TREBLE_CLEF = MnxClef(sign=ClefSign.G, staff_position=-2)
BASS_CLEF = MnxClef(sign=ClefSign.F, staff_position=2)
FOUR_FOUR = MnxTimeSignature(count=4, unit=4)
C_MAJOR = MnxKeySignature(fifths=0)
WHOLE = MnxNoteValue(base=NoteValueBase.Whole)

_STEP_FROM_LETTER: dict[str, NoteStep] = {
    "A": NoteStep.A,
    "B": NoteStep.B,
    "C": NoteStep.C,
    "D": NoteStep.D,
    "E": NoteStep.E,
    "F": NoteStep.F,
    "G": NoteStep.G,
}

# Grand-staff split: upper staff for keynums above this, lower for the rest.
STAFF_SPLIT_KEYNUM = 60


def keynum_to_mnx_pitch(keynum: int) -> MnxPitch:
    """Convert a MIDI key number to an :class:`MnxPitch`."""
    name = keynum_to_pitch(keynum).name
    if len(name) >= 3 and name[1] == "#":
        step = _STEP_FROM_LETTER[name[0]]
        alter = 1.0
        octave = int(name[2:])
    else:
        step = _STEP_FROM_LETTER[name[0]]
        alter = None
        octave = int(name[1:])
    return MnxPitch(step=step, octave=octave, alter=alter)


def _split_keynums(keynums: list[int]) -> tuple[list[int], list[int]]:
    upper = [k for k in keynums if k > STAFF_SPLIT_KEYNUM]
    lower = [k for k in keynums if k <= STAFF_SPLIT_KEYNUM]
    return upper, lower


def _chord_event(keynums: list[int]) -> MnxEvent:
    notes = [MnxNote(pitch=keynum_to_mnx_pitch(k)) for k in sorted(keynums)]
    return MnxEvent.note(duration=WHOLE, notes=notes)


def _staff_sequence(keynums: list[int], voice: str) -> MnxSequence:
    if keynums:
        return MnxSequence(content=[_chord_event(keynums)], voice=voice)
    return MnxSequence(
        content=[MnxEvent.rest(duration=WHOLE)],
        voice=voice,
    )


def chords_to_mnx(chords: list[list[int]]) -> MnxDocument:
    """Build an MNX document with one whole-note chord per measure on a piano grand staff.

    Each inner list is one chord (MIDI key numbers). Notes above key number 60 go on
    the treble staff; notes at or below 60 go on the bass staff.
    """
    if not chords:
        raise ValueError("chords must contain at least one chord")

    global_measures: list[MnxMeasureGlobal] = []
    part_measures: list[MnxPartMeasure] = []

    for i, chord in enumerate(chords):
        is_first = i == 0
        is_last = i == len(chords) - 1

        if is_first:
            global_measures.append(
                MnxMeasureGlobal(time=FOUR_FOUR, key=C_MAJOR),
            )
        elif is_last and len(chords) > 1:
            global_measures.append(
                MnxMeasureGlobal(barline=MnxBarline(kind=BarlineType.Final)),
            )
        else:
            global_measures.append(MnxMeasureGlobal())

        upper, lower = _split_keynums(chord)
        sequences = [
            _staff_sequence(upper, voice="treble"),
            _staff_sequence(lower, voice="bass"),
        ]
        measure = MnxPartMeasure(sequences=sequences)
        if is_first:
            measure = MnxPartMeasure(
                clefs=[
                    MnxPositionedClef(clef=TREBLE_CLEF),
                    MnxPositionedClef(clef=BASS_CLEF),
                ],
                sequences=sequences,
            )
        part_measures.append(measure)

    return MnxDocument(
        mnx=MnxMetadata(version=1),
        global_data=MnxGlobalData(measures=global_measures),
        parts=[
            MnxPart(
                name="Piano",
                measures=part_measures,
                staves=2,
            )
        ],
    )


def save_chords_mnx(
    chords: list[list[int]],
    path: str | Path,
    *,
    pretty: bool = True,
) -> MnxDocument:
    """Write chord voicings to an MNX JSON file and return the document."""
    doc = chords_to_mnx(chords)
    text = doc.to_json_pretty() if pretty else doc.to_json()
    out = Path(path)
    out.write_text(text, encoding="utf-8")
    return doc


if __name__ == "__main__":
    # C major, F major, G major — open the written file in an MNX-aware editor.
    example = [
        [60, 64, 67],  # C4 E4 G4
        [53, 57, 60],  # F3 A3 C4
        [55, 59, 62],  # G3 B3 D4
    ]
    out_path = Path(__file__).with_name("chords.mnx.json")
    save_chords_mnx(example, out_path)
    print(f"Wrote {out_path}")
