"""Tests for the allegro.mnx MNX music notation module.

Each test class corresponds to a canonical MNX example from the specification
(https://w3c-cg.github.io/mnx/docs/mnx-reference/examples/).
"""

import json

import pytest

from allegro.mnx import (
    BarlineType,
    ClefSign,
    MnxBarline,
    MnxClef,
    MnxDocument,
    MnxEvent,
    MnxGlobalData,
    MnxMeasureGlobal,
    MnxMetadata,
    MnxNote,
    MnxNoteValue,
    MnxPart,
    MnxPartMeasure,
    MnxPitch,
    MnxPositionedClef,
    MnxSequence,
    MnxTempo,
    MnxTimeSignature,
    MnxKeySignature,
    NoteStep,
    NoteValueBase,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

TREBLE_CLEF = MnxClef(sign=ClefSign.G, staff_position=-2)
BASS_CLEF = MnxClef(sign=ClefSign.F, staff_position=2)

C_MAJOR_KEY = MnxKeySignature(fifths=0)
FOUR_FOUR = MnxTimeSignature(count=4, unit=4)


def _hello_world_doc() -> MnxDocument:
    """Single C4 whole note in 4/4, treble clef, C major — the MNX hello world."""
    return MnxDocument(
        mnx=MnxMetadata(version=1),
        global_data=MnxGlobalData(measures=[
            MnxMeasureGlobal(time=FOUR_FOUR, key=C_MAJOR_KEY),
        ]),
        parts=[MnxPart(measures=[
            MnxPartMeasure(
                clefs=[MnxPositionedClef(clef=TREBLE_CLEF)],
                sequences=[MnxSequence(content=[
                    MnxEvent.note(
                        duration=MnxNoteValue(base=NoteValueBase.Whole),
                        notes=[MnxNote(pitch=MnxPitch(step=NoteStep.C, octave=4))],
                    )
                ])],
            )
        ])],
    )


# ---------------------------------------------------------------------------
# NoteStep
# ---------------------------------------------------------------------------


class TestNoteStep:
    def test_all_steps_accessible(self):
        steps = [NoteStep.A, NoteStep.B, NoteStep.C, NoteStep.D,
                 NoteStep.E, NoteStep.F, NoteStep.G]
        assert len(steps) == 7

    def test_equality(self):
        assert NoteStep.C == NoteStep.C
        assert NoteStep.C != NoteStep.D


# ---------------------------------------------------------------------------
# NoteValueBase
# ---------------------------------------------------------------------------


class TestNoteValueBase:
    def test_common_values_accessible(self):
        _ = NoteValueBase.Whole
        _ = NoteValueBase.Half
        _ = NoteValueBase.Quarter
        _ = NoteValueBase.Eighth
        _ = NoteValueBase.Sixteenth

    def test_equality(self):
        assert NoteValueBase.Quarter == NoteValueBase.Quarter
        assert NoteValueBase.Quarter != NoteValueBase.Half


# ---------------------------------------------------------------------------
# MnxPitch
# ---------------------------------------------------------------------------


class TestMnxPitch:
    def test_basic(self):
        p = MnxPitch(step=NoteStep.C, octave=4)
        assert p.step == NoteStep.C
        assert p.octave == 4
        assert p.alter is None

    def test_with_alter(self):
        p = MnxPitch(step=NoteStep.F, octave=5, alter=1.0)
        assert p.alter == 1.0

    def test_flat(self):
        p = MnxPitch(step=NoteStep.B, octave=3, alter=-1.0)
        assert p.alter == -1.0


# ---------------------------------------------------------------------------
# MnxNoteValue
# ---------------------------------------------------------------------------


class TestMnxNoteValue:
    def test_whole(self):
        nv = MnxNoteValue(base=NoteValueBase.Whole)
        assert nv.base == NoteValueBase.Whole
        assert nv.dots is None

    def test_dotted_quarter(self):
        nv = MnxNoteValue(base=NoteValueBase.Quarter, dots=1)
        assert nv.dots == 1

    def test_double_dotted_half(self):
        nv = MnxNoteValue(base=NoteValueBase.Half, dots=2)
        assert nv.dots == 2


# ---------------------------------------------------------------------------
# MnxEvent factory methods
# ---------------------------------------------------------------------------


class TestMnxEvent:
    def test_note_factory(self):
        ev = MnxEvent.note(
            duration=MnxNoteValue(base=NoteValueBase.Quarter),
            notes=[MnxNote(pitch=MnxPitch(step=NoteStep.G, octave=4))],
        )
        assert ev.notes is not None
        assert not ev.is_rest

    def test_rest_factory(self):
        ev = MnxEvent.rest(duration=MnxNoteValue(base=NoteValueBase.Half))
        assert ev.is_rest
        assert ev.notes is None

    def test_chord(self):
        ev = MnxEvent.note(
            duration=MnxNoteValue(base=NoteValueBase.Whole),
            notes=[
                MnxNote(pitch=MnxPitch(step=NoteStep.C, octave=4)),
                MnxNote(pitch=MnxPitch(step=NoteStep.E, octave=4)),
                MnxNote(pitch=MnxPitch(step=NoteStep.G, octave=4)),
            ],
        )
        assert len(ev.notes) == 3

    def test_is_rest_false_for_note_event(self):
        ev = MnxEvent.note(
            duration=MnxNoteValue(base=NoteValueBase.Quarter),
            notes=[MnxNote(pitch=MnxPitch(step=NoteStep.C, octave=4))],
        )
        assert not ev.is_rest

    def test_is_rest_true_for_rest_event(self):
        ev = MnxEvent.rest(duration=MnxNoteValue(base=NoteValueBase.Whole))
        assert ev.is_rest


# ---------------------------------------------------------------------------
# MnxDocument measure count validation
# ---------------------------------------------------------------------------


class TestMnxDocumentValidation:
    def test_mismatched_measure_count_raises(self):
        global_data = MnxGlobalData(measures=[
            MnxMeasureGlobal(time=FOUR_FOUR),
            MnxMeasureGlobal(),
        ])
        part_with_one_measure = MnxPart(measures=[
            MnxPartMeasure(sequences=[MnxSequence(content=[
                MnxEvent.note(
                    duration=MnxNoteValue(base=NoteValueBase.Whole),
                    notes=[MnxNote(pitch=MnxPitch(step=NoteStep.C, octave=4))],
                )
            ])])
        ])
        with pytest.raises(ValueError, match="measures"):
            MnxDocument(
                mnx=MnxMetadata(version=1),
                global_data=global_data,
                parts=[part_with_one_measure],
            )


# ---------------------------------------------------------------------------
# Hello world example
# ---------------------------------------------------------------------------


class TestHelloWorld:
    def test_builds_without_error(self):
        doc = _hello_world_doc()
        assert isinstance(doc, MnxDocument)

    def test_metadata(self):
        doc = _hello_world_doc()
        assert doc.mnx.version == 1

    def test_one_measure(self):
        doc = _hello_world_doc()
        assert len(doc.global_data.measures) == 1

    def test_time_signature(self):
        doc = _hello_world_doc()
        ts = doc.global_data.measures[0].time
        assert ts.count == 4
        assert ts.unit == 4

    def test_key_signature(self):
        doc = _hello_world_doc()
        ks = doc.global_data.measures[0].key
        assert ks.fifths == 0

    def test_one_part(self):
        doc = _hello_world_doc()
        assert len(doc.parts) == 1

    def test_treble_clef(self):
        doc = _hello_world_doc()
        clef = doc.parts[0].measures[0].clefs[0].clef
        assert clef.sign == ClefSign.G
        assert clef.staff_position == -2

    def test_single_whole_note(self):
        doc = _hello_world_doc()
        event = doc.parts[0].measures[0].sequences[0].content[0]
        assert event.duration.base == NoteValueBase.Whole
        assert event.notes[0].pitch.step == NoteStep.C
        assert event.notes[0].pitch.octave == 4

    def test_to_json_produces_valid_json(self):
        doc = _hello_world_doc()
        raw = doc.to_json()
        parsed = json.loads(raw)
        assert parsed["mnx"]["version"] == 1

    def test_json_global_key(self):
        """MNX spec: the global data field must be serialized as 'global'."""
        doc = _hello_world_doc()
        parsed = json.loads(doc.to_json())
        assert "global" in parsed

    def test_json_time_signature_structure(self):
        doc = _hello_world_doc()
        parsed = json.loads(doc.to_json())
        measure = parsed["global"]["measures"][0]
        assert measure["time"] == {"count": 4, "unit": 4}

    def test_json_pitch_structure(self):
        doc = _hello_world_doc()
        parsed = json.loads(doc.to_json())
        event = parsed["parts"][0]["measures"][0]["sequences"][0]["content"][0]
        assert event["notes"][0]["pitch"] == {"step": "C", "octave": 4}

    def test_json_clef_camel_case(self):
        """MNX spec: clef staffPosition must be camelCase in JSON."""
        doc = _hello_world_doc()
        parsed = json.loads(doc.to_json())
        clef = parsed["parts"][0]["measures"][0]["clefs"][0]["clef"]
        assert "staffPosition" in clef
        assert clef["staffPosition"] == -2

    def test_json_note_value_base_whole(self):
        doc = _hello_world_doc()
        parsed = json.loads(doc.to_json())
        event = parsed["parts"][0]["measures"][0]["sequences"][0]["content"][0]
        assert event["duration"]["base"] == "whole"

    def test_json_round_trip(self):
        doc = _hello_world_doc()
        restored = MnxDocument.from_json(doc.to_json())
        assert restored.mnx.version == doc.mnx.version
        orig_event = doc.parts[0].measures[0].sequences[0].content[0]
        rest_event = restored.parts[0].measures[0].sequences[0].content[0]
        assert rest_event.duration.base == orig_event.duration.base
        assert rest_event.notes[0].pitch.step == orig_event.notes[0].pitch.step
        assert rest_event.notes[0].pitch.octave == orig_event.notes[0].pitch.octave

    def test_to_json_pretty_is_indented(self):
        doc = _hello_world_doc()
        pretty = doc.to_json_pretty()
        assert "\n" in pretty
        parsed = json.loads(pretty)
        assert "global" in parsed


# ---------------------------------------------------------------------------
# Two-bar C major scale
# ---------------------------------------------------------------------------


class TestTwoBarScale:
    """Eight quarter notes spanning two measures of 4/4."""

    SCALE_STEPS = [
        (NoteStep.C, 4), (NoteStep.D, 4), (NoteStep.E, 4), (NoteStep.F, 4),
        (NoteStep.G, 4), (NoteStep.A, 4), (NoteStep.B, 4), (NoteStep.C, 5),
    ]

    def _make_quarter(self, step: NoteStep, octave: int) -> MnxEvent:
        return MnxEvent.note(
            duration=MnxNoteValue(base=NoteValueBase.Quarter),
            notes=[MnxNote(pitch=MnxPitch(step=step, octave=octave))],
        )

    def _build_doc(self) -> MnxDocument:
        m1_events = [self._make_quarter(s, o) for s, o in self.SCALE_STEPS[:4]]
        m2_events = [self._make_quarter(s, o) for s, o in self.SCALE_STEPS[4:]]
        return MnxDocument(
            mnx=MnxMetadata(version=1),
            global_data=MnxGlobalData(measures=[
                MnxMeasureGlobal(time=FOUR_FOUR, key=C_MAJOR_KEY),
                MnxMeasureGlobal(),
            ]),
            parts=[MnxPart(measures=[
                MnxPartMeasure(
                    clefs=[MnxPositionedClef(clef=TREBLE_CLEF)],
                    sequences=[MnxSequence(content=m1_events)],
                ),
                MnxPartMeasure(
                    sequences=[MnxSequence(content=m2_events)],
                ),
            ])],
        )

    def test_two_measures(self):
        doc = self._build_doc()
        assert len(doc.global_data.measures) == 2
        assert len(doc.parts[0].measures) == 2

    def test_four_notes_per_measure(self):
        doc = self._build_doc()
        assert len(doc.parts[0].measures[0].sequences[0].content) == 4
        assert len(doc.parts[0].measures[1].sequences[0].content) == 4

    def test_first_note_is_c4(self):
        doc = self._build_doc()
        first = doc.parts[0].measures[0].sequences[0].content[0]
        assert first.notes[0].pitch.step == NoteStep.C
        assert first.notes[0].pitch.octave == 4

    def test_last_note_is_c5(self):
        doc = self._build_doc()
        last = doc.parts[0].measures[1].sequences[0].content[-1]
        assert last.notes[0].pitch.step == NoteStep.C
        assert last.notes[0].pitch.octave == 5

    def test_all_quarter_notes(self):
        doc = self._build_doc()
        for measure in doc.parts[0].measures:
            for event in measure.sequences[0].content:
                assert event.duration.base == NoteValueBase.Quarter

    def test_json_round_trip(self):
        doc = self._build_doc()
        restored = MnxDocument.from_json(doc.to_json())
        assert len(restored.parts[0].measures) == 2


# ---------------------------------------------------------------------------
# Multiple parts
# ---------------------------------------------------------------------------


class TestMultipleParts:
    def _build_doc(self) -> MnxDocument:
        measure = MnxMeasureGlobal(time=FOUR_FOUR, key=C_MAJOR_KEY)
        whole_c4 = MnxEvent.note(
            duration=MnxNoteValue(base=NoteValueBase.Whole),
            notes=[MnxNote(pitch=MnxPitch(step=NoteStep.C, octave=4))],
        )
        whole_c3 = MnxEvent.note(
            duration=MnxNoteValue(base=NoteValueBase.Whole),
            notes=[MnxNote(pitch=MnxPitch(step=NoteStep.C, octave=3))],
        )
        return MnxDocument(
            mnx=MnxMetadata(version=1),
            global_data=MnxGlobalData(measures=[measure]),
            parts=[
                MnxPart(
                    name="Violin",
                    measures=[MnxPartMeasure(
                        clefs=[MnxPositionedClef(clef=TREBLE_CLEF)],
                        sequences=[MnxSequence(content=[whole_c4])],
                    )],
                ),
                MnxPart(
                    name="Cello",
                    measures=[MnxPartMeasure(
                        clefs=[MnxPositionedClef(clef=BASS_CLEF)],
                        sequences=[MnxSequence(content=[whole_c3])],
                    )],
                ),
            ],
        )

    def test_two_parts(self):
        doc = self._build_doc()
        assert len(doc.parts) == 2

    def test_part_names(self):
        doc = self._build_doc()
        assert doc.parts[0].name == "Violin"
        assert doc.parts[1].name == "Cello"

    def test_violin_treble_clef(self):
        doc = self._build_doc()
        clef = doc.parts[0].measures[0].clefs[0].clef
        assert clef.sign == ClefSign.G

    def test_cello_bass_clef(self):
        doc = self._build_doc()
        clef = doc.parts[1].measures[0].clefs[0].clef
        assert clef.sign == ClefSign.F

    def test_json_has_two_parts(self):
        doc = self._build_doc()
        parsed = json.loads(doc.to_json())
        assert len(parsed["parts"]) == 2

    def test_json_round_trip(self):
        doc = self._build_doc()
        restored = MnxDocument.from_json(doc.to_json())
        assert len(restored.parts) == 2
        assert restored.parts[0].name == "Violin"
        assert restored.parts[1].name == "Cello"


# ---------------------------------------------------------------------------
# Rests
# ---------------------------------------------------------------------------


class TestRests:
    def test_rest_event_in_document(self):
        doc = MnxDocument(
            mnx=MnxMetadata(version=1),
            global_data=MnxGlobalData(measures=[MnxMeasureGlobal(time=FOUR_FOUR)]),
            parts=[MnxPart(measures=[
                MnxPartMeasure(sequences=[MnxSequence(content=[
                    MnxEvent.rest(duration=MnxNoteValue(base=NoteValueBase.Whole))
                ])])
            ])],
        )
        event = doc.parts[0].measures[0].sequences[0].content[0]
        assert event.is_rest
        assert event.notes is None

    def test_rest_serializes_correctly(self):
        doc = MnxDocument(
            mnx=MnxMetadata(version=1),
            global_data=MnxGlobalData(measures=[MnxMeasureGlobal(time=FOUR_FOUR)]),
            parts=[MnxPart(measures=[
                MnxPartMeasure(sequences=[MnxSequence(content=[
                    MnxEvent.rest(duration=MnxNoteValue(base=NoteValueBase.Whole))
                ])])
            ])],
        )
        parsed = json.loads(doc.to_json())
        event = parsed["parts"][0]["measures"][0]["sequences"][0]["content"][0]
        assert "rest" in event
        assert event["rest"] == {}


# ---------------------------------------------------------------------------
# Barlines
# ---------------------------------------------------------------------------


class TestBarlines:
    def test_final_barline_serialization(self):
        doc = MnxDocument(
            mnx=MnxMetadata(version=1),
            global_data=MnxGlobalData(measures=[
                MnxMeasureGlobal(
                    time=FOUR_FOUR,
                    barline=MnxBarline(kind=BarlineType.Final),
                )
            ]),
            parts=[MnxPart(measures=[
                MnxPartMeasure(sequences=[MnxSequence(content=[
                    MnxEvent.rest(duration=MnxNoteValue(base=NoteValueBase.Whole))
                ])])
            ])],
        )
        parsed = json.loads(doc.to_json())
        barline = parsed["global"]["measures"][0]["barline"]
        assert barline["type"] == "final"


# ---------------------------------------------------------------------------
# Tempo
# ---------------------------------------------------------------------------


class TestTempo:
    def test_tempo_serialization(self):
        doc = MnxDocument(
            mnx=MnxMetadata(version=1),
            global_data=MnxGlobalData(measures=[
                MnxMeasureGlobal(
                    time=FOUR_FOUR,
                    tempos=[MnxTempo(
                        bpm=120.0,
                        value=MnxNoteValue(base=NoteValueBase.Quarter),
                    )],
                )
            ]),
            parts=[MnxPart(measures=[
                MnxPartMeasure(sequences=[MnxSequence(content=[
                    MnxEvent.rest(duration=MnxNoteValue(base=NoteValueBase.Whole))
                ])])
            ])],
        )
        parsed = json.loads(doc.to_json())
        tempo = parsed["global"]["measures"][0]["tempos"][0]
        assert tempo["bpm"] == 120.0
        assert tempo["value"]["base"] == "quarter"


# ---------------------------------------------------------------------------
# NoteValueBase JSON serialization spot-checks
# ---------------------------------------------------------------------------


class TestNoteValueBaseJson:
    @pytest.mark.parametrize(("variant", "expected_json"), [
        (NoteValueBase.Whole, "whole"),
        (NoteValueBase.Half, "half"),
        (NoteValueBase.Quarter, "quarter"),
        (NoteValueBase.Eighth, "eighth"),
        (NoteValueBase.Sixteenth, "16th"),
        (NoteValueBase.ThirtySecond, "32nd"),
        (NoteValueBase.SixtyFourth, "64th"),
        (NoteValueBase.OneTwentyEighth, "128th"),
        (NoteValueBase.Breve, "breve"),
        (NoteValueBase.Longa, "longa"),
    ])
    def test_serializes_to_mnx_string(self, variant, expected_json):
        doc = MnxDocument(
            mnx=MnxMetadata(version=1),
            global_data=MnxGlobalData(measures=[MnxMeasureGlobal(time=FOUR_FOUR)]),
            parts=[MnxPart(measures=[
                MnxPartMeasure(sequences=[MnxSequence(content=[
                    MnxEvent.rest(duration=MnxNoteValue(base=variant))
                ])])
            ])],
        )
        parsed = json.loads(doc.to_json())
        base = parsed["parts"][0]["measures"][0]["sequences"][0]["content"][0]["duration"]["base"]
        assert base == expected_json


# ---------------------------------------------------------------------------
# Multiple voices
# ---------------------------------------------------------------------------


class TestMultipleVoices:
    def test_two_voices_in_one_measure(self):
        soprano = MnxEvent.note(
            duration=MnxNoteValue(base=NoteValueBase.Half),
            notes=[MnxNote(pitch=MnxPitch(step=NoteStep.E, octave=5))],
        )
        alto = MnxEvent.note(
            duration=MnxNoteValue(base=NoteValueBase.Half),
            notes=[MnxNote(pitch=MnxPitch(step=NoteStep.C, octave=5))],
        )
        doc = MnxDocument(
            mnx=MnxMetadata(version=1),
            global_data=MnxGlobalData(measures=[
                MnxMeasureGlobal(time=MnxTimeSignature(count=2, unit=2))
            ]),
            parts=[MnxPart(measures=[
                MnxPartMeasure(
                    clefs=[MnxPositionedClef(clef=TREBLE_CLEF)],
                    sequences=[
                        MnxSequence(content=[soprano], voice="v1"),
                        MnxSequence(content=[alto], voice="v2"),
                    ],
                )
            ])],
        )
        measure = doc.parts[0].measures[0]
        assert len(measure.sequences) == 2
        assert measure.sequences[0].voice == "v1"
        assert measure.sequences[1].voice == "v2"

    def test_voices_in_json(self):
        soprano = MnxEvent.note(
            duration=MnxNoteValue(base=NoteValueBase.Whole),
            notes=[MnxNote(pitch=MnxPitch(step=NoteStep.G, octave=4))],
        )
        bass = MnxEvent.note(
            duration=MnxNoteValue(base=NoteValueBase.Whole),
            notes=[MnxNote(pitch=MnxPitch(step=NoteStep.C, octave=3))],
        )
        doc = MnxDocument(
            mnx=MnxMetadata(version=1),
            global_data=MnxGlobalData(measures=[MnxMeasureGlobal(time=FOUR_FOUR)]),
            parts=[MnxPart(measures=[
                MnxPartMeasure(sequences=[
                    MnxSequence(content=[soprano], voice="upper"),
                    MnxSequence(content=[bass], voice="lower"),
                ])
            ])],
        )
        parsed = json.loads(doc.to_json())
        seqs = parsed["parts"][0]["measures"][0]["sequences"]
        assert seqs[0]["voice"] == "upper"
        assert seqs[1]["voice"] == "lower"


# ---------------------------------------------------------------------------
# Grand staff (piano)
# ---------------------------------------------------------------------------


class TestGrandStaff:
    def test_staves_attribute(self):
        treble_note = MnxEvent.note(
            duration=MnxNoteValue(base=NoteValueBase.Whole),
            notes=[MnxNote(pitch=MnxPitch(step=NoteStep.C, octave=5))],
        )
        bass_note = MnxEvent.note(
            duration=MnxNoteValue(base=NoteValueBase.Whole),
            notes=[MnxNote(pitch=MnxPitch(step=NoteStep.C, octave=3))],
        )
        doc = MnxDocument(
            mnx=MnxMetadata(version=1),
            global_data=MnxGlobalData(measures=[MnxMeasureGlobal(time=FOUR_FOUR)]),
            parts=[MnxPart(
                name="Piano",
                staves=2,
                measures=[MnxPartMeasure(
                    clefs=[
                        MnxPositionedClef(clef=TREBLE_CLEF),
                        MnxPositionedClef(clef=BASS_CLEF),
                    ],
                    sequences=[
                        MnxSequence(content=[treble_note], voice="right"),
                        MnxSequence(content=[bass_note], voice="left"),
                    ],
                )],
            )],
        )
        assert doc.parts[0].staves == 2

    def test_grand_staff_json(self):
        note = MnxEvent.note(
            duration=MnxNoteValue(base=NoteValueBase.Whole),
            notes=[MnxNote(pitch=MnxPitch(step=NoteStep.C, octave=4))],
        )
        doc = MnxDocument(
            mnx=MnxMetadata(version=1),
            global_data=MnxGlobalData(measures=[MnxMeasureGlobal(time=FOUR_FOUR)]),
            parts=[MnxPart(
                name="Piano",
                staves=2,
                measures=[MnxPartMeasure(
                    sequences=[MnxSequence(content=[note])],
                )],
            )],
        )
        parsed = json.loads(doc.to_json())
        assert parsed["parts"][0]["staves"] == 2
        assert parsed["parts"][0]["name"] == "Piano"


# ---------------------------------------------------------------------------
# Dotted notes
# ---------------------------------------------------------------------------


class TestDottedNotes:
    def test_dotted_quarter_serialization(self):
        doc = MnxDocument(
            mnx=MnxMetadata(version=1),
            global_data=MnxGlobalData(measures=[MnxMeasureGlobal(time=FOUR_FOUR)]),
            parts=[MnxPart(measures=[
                MnxPartMeasure(sequences=[MnxSequence(content=[
                    MnxEvent.note(
                        duration=MnxNoteValue(base=NoteValueBase.Quarter, dots=1),
                        notes=[MnxNote(pitch=MnxPitch(step=NoteStep.A, octave=4))],
                    ),
                    MnxEvent.rest(duration=MnxNoteValue(base=NoteValueBase.Eighth)),
                ])])
            ])],
        )
        parsed = json.loads(doc.to_json())
        first = parsed["parts"][0]["measures"][0]["sequences"][0]["content"][0]
        assert first["duration"]["dots"] == 1

    def test_undotted_note_omits_dots(self):
        doc = MnxDocument(
            mnx=MnxMetadata(version=1),
            global_data=MnxGlobalData(measures=[MnxMeasureGlobal(time=FOUR_FOUR)]),
            parts=[MnxPart(measures=[
                MnxPartMeasure(sequences=[MnxSequence(content=[
                    MnxEvent.rest(duration=MnxNoteValue(base=NoteValueBase.Whole))
                ])])
            ])],
        )
        parsed = json.loads(doc.to_json())
        dur = parsed["parts"][0]["measures"][0]["sequences"][0]["content"][0]["duration"]
        assert "dots" not in dur
