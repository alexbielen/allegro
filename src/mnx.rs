use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};

use crate::py_stub::{gen_stub_pyclass, gen_stub_pyclass_enum, gen_stub_pymethods};

// ============ Enums ============

/// The diatonic pitch step (letter name) of a note.
#[gen_stub_pyclass_enum]
#[pyclass(eq)]
#[derive(Clone, Copy, PartialEq, Serialize, Deserialize, Debug)]
pub enum NoteStep {
    /// The note A.
    #[pyo3(name = "A")]
    #[serde(rename = "A")]
    A,
    /// The note B.
    #[pyo3(name = "B")]
    #[serde(rename = "B")]
    B,
    /// The note C.
    #[pyo3(name = "C")]
    #[serde(rename = "C")]
    C,
    /// The note D.
    #[pyo3(name = "D")]
    #[serde(rename = "D")]
    D,
    /// The note E.
    #[pyo3(name = "E")]
    #[serde(rename = "E")]
    E,
    /// The note F.
    #[pyo3(name = "F")]
    #[serde(rename = "F")]
    F,
    /// The note G.
    #[pyo3(name = "G")]
    #[serde(rename = "G")]
    G,
}

/// The base rhythmic duration of a note, without augmentation dots.
#[gen_stub_pyclass_enum]
#[pyclass(eq)]
#[derive(Clone, Copy, PartialEq, Serialize, Deserialize, Debug)]
pub enum NoteValueBase {
    /// Maxima (8 whole notes).
    #[pyo3(name = "Maxima")]
    #[serde(rename = "maxima")]
    Maxima,
    /// Longa (4 whole notes).
    #[pyo3(name = "Longa")]
    #[serde(rename = "longa")]
    Longa,
    /// Duplex Maxima (16 whole notes).
    #[pyo3(name = "DuplexMaxima")]
    #[serde(rename = "duplexMaxima")]
    DuplexMaxima,
    /// Breve (2 whole notes).
    #[pyo3(name = "Breve")]
    #[serde(rename = "breve")]
    Breve,
    /// Whole note.
    #[pyo3(name = "Whole")]
    #[serde(rename = "whole")]
    Whole,
    /// Half note.
    #[pyo3(name = "Half")]
    #[serde(rename = "half")]
    Half,
    /// Quarter note.
    #[pyo3(name = "Quarter")]
    #[serde(rename = "quarter")]
    Quarter,
    /// Eighth note.
    #[pyo3(name = "Eighth")]
    #[serde(rename = "eighth")]
    Eighth,
    /// 16th note.
    #[pyo3(name = "Sixteenth")]
    #[serde(rename = "16th")]
    Sixteenth,
    /// 32nd note.
    #[pyo3(name = "ThirtySecond")]
    #[serde(rename = "32nd")]
    ThirtySecond,
    /// 64th note.
    #[pyo3(name = "SixtyFourth")]
    #[serde(rename = "64th")]
    SixtyFourth,
    /// 128th note.
    #[pyo3(name = "OneTwentyEighth")]
    #[serde(rename = "128th")]
    OneTwentyEighth,
    /// 256th note.
    #[pyo3(name = "TwoFiftySixth")]
    #[serde(rename = "256th")]
    TwoFiftySixth,
    /// 512th note.
    #[pyo3(name = "FiveTwelfth")]
    #[serde(rename = "512th")]
    FiveTwelfth,
    /// 1024th note.
    #[pyo3(name = "TenTwentyFourth")]
    #[serde(rename = "1024th")]
    TenTwentyFourth,
    /// 2048th note.
    #[pyo3(name = "TwoThousandFortyEighth")]
    #[serde(rename = "2048th")]
    TwoThousandFortyEighth,
    /// 4096th note.
    #[pyo3(name = "FourThousandNinetySixth")]
    #[serde(rename = "4096th")]
    FourThousandNinetySixth,
}

/// The sign used for a clef.
#[gen_stub_pyclass_enum]
#[pyclass(eq)]
#[derive(Clone, Copy, PartialEq, Serialize, Deserialize, Debug)]
pub enum ClefSign {
    /// Treble (G) clef.
    #[pyo3(name = "G")]
    #[serde(rename = "G")]
    G,
    /// Bass (F) clef.
    #[pyo3(name = "F")]
    #[serde(rename = "F")]
    F,
    /// Alto/tenor (C) clef.
    #[pyo3(name = "C")]
    #[serde(rename = "C")]
    C,
    /// Percussion clef.
    #[pyo3(name = "Percussion")]
    #[serde(rename = "percussion")]
    Percussion,
    /// Tab clef (for guitar tablature).
    #[pyo3(name = "Tab")]
    #[serde(rename = "tab")]
    Tab,
}

/// The visual style of a barline.
#[gen_stub_pyclass_enum]
#[pyclass(eq)]
#[derive(Clone, Copy, PartialEq, Serialize, Deserialize, Debug)]
pub enum BarlineType {
    /// Standard single barline.
    #[pyo3(name = "Regular")]
    #[serde(rename = "regular")]
    Regular,
    /// Final double barline (thin-thick).
    #[pyo3(name = "Final")]
    #[serde(rename = "final")]
    Final,
    /// Double barline (thin-thin).
    #[pyo3(name = "Double")]
    #[serde(rename = "double")]
    Double,
    /// Dashed barline.
    #[pyo3(name = "Dashed")]
    #[serde(rename = "dashed")]
    Dashed,
    /// Dotted barline.
    #[pyo3(name = "Dotted")]
    #[serde(rename = "dotted")]
    Dotted,
    /// Tick barline.
    #[pyo3(name = "Tick")]
    #[serde(rename = "tick")]
    Tick,
    /// Short barline.
    #[pyo3(name = "Short")]
    #[serde(rename = "short")]
    Short,
}

// ============ Leaf structs ============

/// The sounded pitch of a note: step, octave, and optional chromatic alteration.
///
/// Pitches are represented using the diatonic step (C–G), a Helmholtz octave
/// number (4 = middle C octave), and an optional ``alter`` value in semitones
/// (e.g. ``1.0`` for sharp, ``-1.0`` for flat).
#[gen_stub_pyclass]
#[pyclass]
#[derive(Clone, Serialize, Deserialize, Debug, PartialEq)]
pub struct MnxPitch {
    pub step: NoteStep,
    pub octave: i32,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub alter: Option<f64>,
}

#[gen_stub_pymethods]
#[pymethods]
impl MnxPitch {
    /// Create a new pitch.
    ///
    /// Args:
    ///     step (NoteStep): The diatonic pitch step (A–G).
    ///     octave (int): The octave number (4 = middle C octave).
    ///     alter (float | None): Chromatic alteration in semitones
    ///         (``1.0`` for sharp, ``-1.0`` for flat). Defaults to ``None``.
    ///
    /// Returns:
    ///     MnxPitch
    #[new]
    #[pyo3(signature = (step, octave, alter = None))]
    pub fn new(step: NoteStep, octave: i32, alter: Option<f64>) -> Self {
        Self { step, octave, alter }
    }

    /// The diatonic pitch step.
    #[getter]
    fn step(&self) -> NoteStep {
        self.step
    }

    /// The octave number (4 = middle C octave).
    #[getter]
    fn octave(&self) -> i32 {
        self.octave
    }

    /// Chromatic alteration in semitones, if any.
    #[getter]
    fn alter(&self) -> Option<f64> {
        self.alter
    }
}

/// A rhythmic note value: a base duration plus optional augmentation dots.
///
/// Examples:
///     A dotted quarter note: ``MnxNoteValue(base=NoteValueBase.Quarter, dots=1)``
///
///     A whole note: ``MnxNoteValue(base=NoteValueBase.Whole)``
#[gen_stub_pyclass]
#[pyclass]
#[derive(Clone, Serialize, Deserialize, Debug, PartialEq)]
pub struct MnxNoteValue {
    pub base: NoteValueBase,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub dots: Option<u32>,
}

#[gen_stub_pymethods]
#[pymethods]
impl MnxNoteValue {
    /// Create a new note value.
    ///
    /// Args:
    ///     base (NoteValueBase): The base rhythmic duration.
    ///     dots (int | None): Number of augmentation dots (0–5). Defaults to ``None``.
    ///
    /// Returns:
    ///     MnxNoteValue
    #[new]
    #[pyo3(signature = (base, dots = None))]
    pub fn new(base: NoteValueBase, dots: Option<u32>) -> Self {
        Self { base, dots }
    }

    /// The base rhythmic duration.
    #[getter]
    fn base(&self) -> NoteValueBase {
        self.base
    }

    /// Number of augmentation dots, if any.
    #[getter]
    fn dots(&self) -> Option<u32> {
        self.dots
    }
}

/// A rest within an event. Serializes as an empty object ``{}``.
#[gen_stub_pyclass]
#[pyclass]
#[derive(Clone, Serialize, Deserialize, Debug, PartialEq)]
pub struct MnxRest {}

#[gen_stub_pymethods]
#[pymethods]
impl MnxRest {
    /// Create a rest.
    ///
    /// Returns:
    ///     MnxRest
    #[new]
    pub fn new() -> Self {
        Self {}
    }
}

impl Default for MnxRest {
    fn default() -> Self {
        Self::new()
    }
}

/// A single note within an event, identified by its sounded pitch.
///
/// Future attributes (ties, staff override, accidental display) can be added
/// without breaking existing documents.
#[gen_stub_pyclass]
#[pyclass]
#[derive(Clone, Serialize, Deserialize, Debug, PartialEq)]
pub struct MnxNote {
    pub pitch: MnxPitch,
}

#[gen_stub_pymethods]
#[pymethods]
impl MnxNote {
    /// Create a note.
    ///
    /// Args:
    ///     pitch (MnxPitch): The sounded pitch of this note.
    ///
    /// Returns:
    ///     MnxNote
    #[new]
    pub fn new(pitch: MnxPitch) -> Self {
        Self { pitch }
    }

    /// The sounded pitch of this note.
    #[getter]
    fn pitch(&self) -> MnxPitch {
        self.pitch.clone()
    }
}

// ============ Event / Sequence ============

/// A discrete musical event: a set of simultaneous pitched notes, or a rest.
///
/// Construct via the named factory methods rather than directly:
///
/// - :meth:`MnxEvent.note` — one or more simultaneous pitches (chord or single note)
/// - :meth:`MnxEvent.rest` — a silent rest
///
/// This design makes intent unambiguous at the call site and eliminates
/// invalid states (neither notes nor rest; both notes and rest).
///
/// Extension note: when tuplet and grace-note sequence items are added they
/// will implement a shared ``SequenceItem`` trait alongside ``MnxEvent``.
#[gen_stub_pyclass]
#[pyclass]
#[derive(Clone, Serialize, Deserialize, Debug, PartialEq)]
pub struct MnxEvent {
    pub duration: MnxNoteValue,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub notes: Option<Vec<MnxNote>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub rest: Option<MnxRest>,
}

#[gen_stub_pymethods]
#[pymethods]
impl MnxEvent {
    /// Create a note event containing one or more simultaneous pitches.
    ///
    /// A single-element list produces a single note; multiple elements produce
    /// a chord.
    ///
    /// Args:
    ///     duration (MnxNoteValue): The rhythmic duration.
    ///     notes (list[MnxNote]): One or more notes sounding together.
    ///
    /// Returns:
    ///     MnxEvent
    ///
    /// Examples:
    ///     Single note::
    ///
    ///         event = MnxEvent.note(
    ///             duration=MnxNoteValue(base=NoteValueBase.Quarter),
    ///             notes=[MnxNote(pitch=MnxPitch(step=NoteStep.C, octave=4))],
    ///         )
    ///
    ///     Chord::
    ///
    ///         event = MnxEvent.note(
    ///             duration=MnxNoteValue(base=NoteValueBase.Half),
    ///             notes=[
    ///                 MnxNote(pitch=MnxPitch(step=NoteStep.C, octave=4)),
    ///                 MnxNote(pitch=MnxPitch(step=NoteStep.E, octave=4)),
    ///                 MnxNote(pitch=MnxPitch(step=NoteStep.G, octave=4)),
    ///             ],
    ///         )
    #[staticmethod]
    pub fn note(duration: MnxNoteValue, notes: Vec<MnxNote>) -> Self {
        Self { duration, notes: Some(notes), rest: None }
    }

    /// Create a rest event.
    ///
    /// Args:
    ///     duration (MnxNoteValue): The rhythmic duration of the rest.
    ///
    /// Returns:
    ///     MnxEvent
    ///
    /// Examples:
    ///     Whole-note rest::
    ///
    ///         event = MnxEvent.rest(duration=MnxNoteValue(base=NoteValueBase.Whole))
    #[staticmethod]
    pub fn rest(duration: MnxNoteValue) -> Self {
        Self { duration, notes: None, rest: Some(MnxRest {}) }
    }

    /// The rhythmic duration of this event.
    #[getter]
    fn duration(&self) -> MnxNoteValue {
        self.duration.clone()
    }

    /// Notes sounding in this event, or ``None`` if this is a rest.
    #[getter]
    fn notes(&self) -> Option<Vec<MnxNote>> {
        self.notes.clone()
    }

    /// ``True`` if this event is a rest; ``False`` if it contains notes.
    #[getter]
    fn is_rest(&self) -> bool {
        self.rest.is_some()
    }
}

/// An ordered sequence of events forming a single polyphonic voice within a measure.
///
/// All events in a sequence must cover the full duration of the measure
/// when summed. Use the ``voice`` attribute to distinguish multiple sequences
/// (voices) within the same measure.
#[gen_stub_pyclass]
#[pyclass]
#[derive(Clone, Serialize, Deserialize, Debug, PartialEq)]
pub struct MnxSequence {
    pub content: Vec<MnxEvent>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub voice: Option<String>,
}

#[gen_stub_pymethods]
#[pymethods]
impl MnxSequence {
    /// Create a sequence.
    ///
    /// Args:
    ///     content (list[MnxEvent]): The ordered events in this voice.
    ///     voice (str | None): An opaque identifier for this voice. Sequences
    ///         sharing the same ``voice`` value across measures belong to the
    ///         same voice. Defaults to ``None``.
    ///
    /// Returns:
    ///     MnxSequence
    #[new]
    #[pyo3(signature = (content, voice = None))]
    pub fn new(content: Vec<MnxEvent>, voice: Option<String>) -> Self {
        Self { content, voice }
    }

    /// The ordered events in this voice.
    #[getter]
    fn content(&self) -> Vec<MnxEvent> {
        self.content.clone()
    }

    /// The voice identifier, if any.
    #[getter]
    fn voice(&self) -> Option<String> {
        self.voice.clone()
    }
}

// ============ Notation primitives ============

/// A clef definition: sign, staff line position, and optional octave transposition.
///
/// The ``staff_position`` follows MNX convention: a standard G clef is drawn
/// at position ``-2`` (the second line from the bottom).
#[gen_stub_pyclass]
#[pyclass]
#[derive(Clone, Serialize, Deserialize, Debug, PartialEq)]
#[serde(rename_all = "camelCase")]
pub struct MnxClef {
    pub sign: ClefSign,
    pub staff_position: i32,
}

#[gen_stub_pymethods]
#[pymethods]
impl MnxClef {
    /// Create a clef.
    ///
    /// Args:
    ///     sign (ClefSign): The clef sign (G, F, C, …).
    ///     staff_position (int): Staff position at which the clef glyph is drawn.
    ///         A standard treble clef uses ``-2``. A standard bass clef uses ``2``.
    ///
    /// Returns:
    ///     MnxClef
    #[new]
    pub fn new(sign: ClefSign, staff_position: i32) -> Self {
        Self { sign, staff_position }
    }

    /// The clef sign.
    #[getter]
    fn sign(&self) -> ClefSign {
        self.sign
    }

    /// The staff position at which the clef glyph is drawn.
    #[getter]
    fn staff_position(&self) -> i32 {
        self.staff_position
    }
}

/// A clef placed at a specific position within a measure.
///
/// If no ``position`` is supplied the clef is assumed to be at the start of
/// the measure.
#[gen_stub_pyclass]
#[pyclass]
#[derive(Clone, Serialize, Deserialize, Debug, PartialEq)]
pub struct MnxPositionedClef {
    pub clef: MnxClef,
}

#[gen_stub_pymethods]
#[pymethods]
impl MnxPositionedClef {
    /// Create a positioned clef.
    ///
    /// Args:
    ///     clef (MnxClef): The clef definition.
    ///
    /// Returns:
    ///     MnxPositionedClef
    #[new]
    pub fn new(clef: MnxClef) -> Self {
        Self { clef }
    }

    /// The clef definition.
    #[getter]
    fn clef(&self) -> MnxClef {
        self.clef.clone()
    }
}

/// A key signature defined by its distance in fifths from C major / A minor.
///
/// Positive values indicate sharps; negative values indicate flats.
/// Zero indicates C major / A minor (no accidentals).
///
/// Examples:
///     G major (1 sharp): ``MnxKeySignature(fifths=1)``
///
///     F major (1 flat): ``MnxKeySignature(fifths=-1)``
#[gen_stub_pyclass]
#[pyclass]
#[derive(Clone, Serialize, Deserialize, Debug, PartialEq)]
pub struct MnxKeySignature {
    pub fifths: i32,
}

#[gen_stub_pymethods]
#[pymethods]
impl MnxKeySignature {
    /// Create a key signature.
    ///
    /// Args:
    ///     fifths (int): Distance in perfect fifths from C (positive = sharps,
    ///         negative = flats).
    ///
    /// Returns:
    ///     MnxKeySignature
    #[new]
    pub fn new(fifths: i32) -> Self {
        Self { fifths }
    }

    /// Distance in fifths from C major / A minor.
    #[getter]
    fn fifths(&self) -> i32 {
        self.fifths
    }
}

/// A time signature expressed as beat count over beat unit.
///
/// Examples:
///     4/4 time: ``MnxTimeSignature(count=4, unit=4)``
///
///     6/8 time: ``MnxTimeSignature(count=6, unit=8)``
#[gen_stub_pyclass]
#[pyclass]
#[derive(Clone, Serialize, Deserialize, Debug, PartialEq)]
pub struct MnxTimeSignature {
    pub count: u32,
    pub unit: u32,
}

#[gen_stub_pymethods]
#[pymethods]
impl MnxTimeSignature {
    /// Create a time signature.
    ///
    /// Args:
    ///     count (int): Number of beats (top number).
    ///     unit (int): Beat unit as a power of two (bottom number, e.g. 4 or 8).
    ///
    /// Returns:
    ///     MnxTimeSignature
    #[new]
    pub fn new(count: u32, unit: u32) -> Self {
        Self { count, unit }
    }

    /// The beat count (top number of the time signature).
    #[getter]
    fn count(&self) -> u32 {
        self.count
    }

    /// The beat unit (bottom number of the time signature).
    #[getter]
    fn unit(&self) -> u32 {
        self.unit
    }
}

/// A barline drawn at the end of a measure.
///
/// If omitted from a measure, consuming software infers ``Regular`` for all
/// measures except the last, which defaults to ``Final``.
#[gen_stub_pyclass]
#[pyclass]
#[derive(Clone, Serialize, Deserialize, Debug, PartialEq)]
pub struct MnxBarline {
    /// The visual style of the barline.
    #[serde(rename = "type")]
    pub kind: BarlineType,
}

#[gen_stub_pymethods]
#[pymethods]
impl MnxBarline {
    /// Create a barline.
    ///
    /// Args:
    ///     kind (BarlineType): The visual style of the barline.
    ///
    /// Returns:
    ///     MnxBarline
    #[new]
    pub fn new(kind: BarlineType) -> Self {
        Self { kind }
    }

    /// The visual style of this barline.
    #[getter]
    fn kind(&self) -> BarlineType {
        self.kind
    }
}

/// A tempo marking expressed as beats-per-minute for a given note value.
///
/// Examples:
///     Quarter note = 120 bpm: ``MnxTempo(bpm=120.0, value=MnxNoteValue(base=NoteValueBase.Quarter))``
#[gen_stub_pyclass]
#[pyclass]
#[derive(Clone, Serialize, Deserialize, Debug, PartialEq)]
pub struct MnxTempo {
    pub bpm: f64,
    pub value: MnxNoteValue,
}

#[gen_stub_pymethods]
#[pymethods]
impl MnxTempo {
    /// Create a tempo marking.
    ///
    /// Args:
    ///     bpm (float): Beats per minute.
    ///     value (MnxNoteValue): The note value that receives one beat.
    ///
    /// Returns:
    ///     MnxTempo
    #[new]
    pub fn new(bpm: f64, value: MnxNoteValue) -> Self {
        Self { bpm, value }
    }

    /// Beats per minute.
    #[getter]
    fn bpm(&self) -> f64 {
        self.bpm
    }

    /// The note value that receives one beat.
    #[getter]
    fn value(&self) -> MnxNoteValue {
        self.value.clone()
    }
}

// ============ Document structure ============

/// Global measure metadata shared across all parts.
///
/// Each ``MnxMeasureGlobal`` corresponds to one measure in every part.
/// Only attributes that change need to appear; omitted attributes are
/// inherited from the previous measure or left to the consuming application.
#[gen_stub_pyclass]
#[pyclass]
#[derive(Clone, Serialize, Deserialize, Debug, PartialEq)]
pub struct MnxMeasureGlobal {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub time: Option<MnxTimeSignature>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub key: Option<MnxKeySignature>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub barline: Option<MnxBarline>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub tempos: Option<Vec<MnxTempo>>,
}

#[gen_stub_pymethods]
#[pymethods]
impl MnxMeasureGlobal {
    /// Create global measure metadata.
    ///
    /// Args:
    ///     time (MnxTimeSignature | None): Time signature. Supply only in the
    ///         first measure or when it changes.
    ///     key (MnxKeySignature | None): Key signature. Supply only in the
    ///         first measure or when it changes.
    ///     barline (MnxBarline | None): Barline at the end of this measure.
    ///     tempos (list[MnxTempo] | None): Tempo markings at the start of
    ///         this measure.
    ///
    /// Returns:
    ///     MnxMeasureGlobal
    #[new]
    #[pyo3(signature = (time = None, key = None, barline = None, tempos = None))]
    pub fn new(
        time: Option<MnxTimeSignature>,
        key: Option<MnxKeySignature>,
        barline: Option<MnxBarline>,
        tempos: Option<Vec<MnxTempo>>,
    ) -> Self {
        Self { time, key, barline, tempos }
    }

    /// The time signature for this measure, if set.
    #[getter]
    fn time(&self) -> Option<MnxTimeSignature> {
        self.time.clone()
    }

    /// The key signature for this measure, if set.
    #[getter]
    fn key(&self) -> Option<MnxKeySignature> {
        self.key.clone()
    }

    /// The barline at the end of this measure, if set.
    #[getter]
    fn barline(&self) -> Option<MnxBarline> {
        self.barline.clone()
    }

    /// Tempo markings at the start of this measure, if any.
    #[getter]
    fn tempos(&self) -> Option<Vec<MnxTempo>> {
        self.tempos.clone()
    }
}

/// The global section of an MNX document: one ``MnxMeasureGlobal`` per measure.
#[gen_stub_pyclass]
#[pyclass]
#[derive(Clone, Serialize, Deserialize, Debug, PartialEq)]
pub struct MnxGlobalData {
    pub measures: Vec<MnxMeasureGlobal>,
}

#[gen_stub_pymethods]
#[pymethods]
impl MnxGlobalData {
    /// Create the global data section.
    ///
    /// Args:
    ///     measures (list[MnxMeasureGlobal]): One entry per measure in the
    ///         document. Every part must have the same number of measures.
    ///
    /// Returns:
    ///     MnxGlobalData
    #[new]
    pub fn new(measures: Vec<MnxMeasureGlobal>) -> Self {
        Self { measures }
    }

    /// The list of per-measure global metadata objects.
    #[getter]
    fn measures(&self) -> Vec<MnxMeasureGlobal> {
        self.measures.clone()
    }
}

/// MNX document metadata: currently just the format version number.
#[gen_stub_pyclass]
#[pyclass]
#[derive(Clone, Serialize, Deserialize, Debug, PartialEq)]
pub struct MnxMetadata {
    pub version: u32,
}

#[gen_stub_pymethods]
#[pymethods]
impl MnxMetadata {
    /// Create MNX metadata.
    ///
    /// Args:
    ///     version (int): The MNX version number (use ``1`` for the current draft).
    ///
    /// Returns:
    ///     MnxMetadata
    #[new]
    pub fn new(version: u32) -> Self {
        Self { version }
    }

    /// The MNX version number.
    #[getter]
    fn version(&self) -> u32 {
        self.version
    }
}

/// A single measure within a part, containing sequences of events and optional clef changes.
#[gen_stub_pyclass]
#[pyclass]
#[derive(Clone, Serialize, Deserialize, Debug, PartialEq)]
pub struct MnxPartMeasure {
    pub sequences: Vec<MnxSequence>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub clefs: Option<Vec<MnxPositionedClef>>,
}

#[gen_stub_pymethods]
#[pymethods]
impl MnxPartMeasure {
    /// Create a part measure.
    ///
    /// Args:
    ///     sequences (list[MnxSequence]): One sequence per voice. A typical
    ///         single-voice measure has exactly one sequence.
    ///     clefs (list[MnxPositionedClef] | None): Clef changes within this
    ///         measure. A clef at the start of the first measure sets the initial
    ///         clef for the part.
    ///
    /// Returns:
    ///     MnxPartMeasure
    #[new]
    #[pyo3(signature = (sequences, clefs = None))]
    pub fn new(sequences: Vec<MnxSequence>, clefs: Option<Vec<MnxPositionedClef>>) -> Self {
        Self { sequences, clefs }
    }

    /// The sequences (voices) in this measure.
    #[getter]
    fn sequences(&self) -> Vec<MnxSequence> {
        self.sequences.clone()
    }

    /// Clef changes in this measure, if any.
    #[getter]
    fn clefs(&self) -> Option<Vec<MnxPositionedClef>> {
        self.clefs.clone()
    }
}

/// A single instrument part containing one measure per global measure.
#[gen_stub_pyclass]
#[pyclass]
#[derive(Clone, Serialize, Deserialize, Debug, PartialEq)]
pub struct MnxPart {
    pub measures: Vec<MnxPartMeasure>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub name: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub staves: Option<u32>,
}

#[gen_stub_pymethods]
#[pymethods]
impl MnxPart {
    /// Create a part.
    ///
    /// Args:
    ///     measures (list[MnxPartMeasure]): One measure per global measure.
    ///         The length must match ``MnxGlobalData.measures``.
    ///     name (str | None): Display name for the part (e.g. ``"Violin I"``).
    ///     staves (int | None): Number of staves (default ``1``; use ``2`` for
    ///         grand staff as in piano music).
    ///
    /// Returns:
    ///     MnxPart
    #[new]
    #[pyo3(signature = (measures, name = None, staves = None))]
    pub fn new(measures: Vec<MnxPartMeasure>, name: Option<String>, staves: Option<u32>) -> Self {
        Self { measures, name, staves }
    }

    /// The measures of this part.
    #[getter]
    fn measures(&self) -> Vec<MnxPartMeasure> {
        self.measures.clone()
    }

    /// The display name of this part, if set.
    #[getter]
    fn name(&self) -> Option<String> {
        self.name.clone()
    }

    /// The number of staves in this part, if set.
    #[getter]
    fn staves(&self) -> Option<u32> {
        self.staves
    }
}

/// The root MNX document object.
///
/// An ``MnxDocument`` contains everything needed to represent a complete piece
/// of music: metadata, global measure data (time/key signatures, tempos), and
/// one or more parts.
///
/// Use :meth:`to_json` or :meth:`to_json_pretty` to produce MNX-compliant JSON.
/// Use :meth:`from_json` to parse an existing MNX JSON string.
///
/// Examples:
///     Hello world — C4 whole note, 4/4, treble clef::
///
///         from allegro.mnx import (
///             MnxDocument, MnxMetadata, MnxGlobalData, MnxMeasureGlobal,
///             MnxPart, MnxPartMeasure, MnxSequence, MnxEvent,
///             MnxNote, MnxPitch, MnxNoteValue, MnxClef, MnxPositionedClef,
///             MnxKeySignature, MnxTimeSignature,
///             NoteStep, NoteValueBase, ClefSign,
///         )
///
///         doc = MnxDocument(
///             mnx=MnxMetadata(version=1),
///             global_data=MnxGlobalData(measures=[
///                 MnxMeasureGlobal(
///                     time=MnxTimeSignature(count=4, unit=4),
///                     key=MnxKeySignature(fifths=0),
///                 )
///             ]),
///             parts=[MnxPart(measures=[
///                 MnxPartMeasure(
///                     clefs=[MnxPositionedClef(clef=MnxClef(
///                         sign=ClefSign.G, staff_position=-2
///                     ))],
///                     sequences=[MnxSequence(content=[
///                     sequences=[MnxSequence(content=[
///                         MnxEvent.note(
///                             duration=MnxNoteValue(base=NoteValueBase.Whole),
///                             notes=[MnxNote(pitch=MnxPitch(
///                                 step=NoteStep.C, octave=4
///                             ))],
///                         )
///                     ])],
///                 )
///             ])],
///         )
///         print(doc.to_json_pretty())
#[gen_stub_pyclass]
#[pyclass]
#[derive(Clone, Serialize, Deserialize, Debug, PartialEq)]
pub struct MnxDocument {
    pub mnx: MnxMetadata,
    #[serde(rename = "global")]
    pub global_data: MnxGlobalData,
    pub parts: Vec<MnxPart>,
}

#[gen_stub_pymethods]
#[pymethods]
impl MnxDocument {
    /// Create an MNX document.
    ///
    /// Args:
    ///     mnx (MnxMetadata): Document metadata (includes the MNX version).
    ///     global_data (MnxGlobalData): Global measure data shared across all
    ///         parts (time/key signatures, tempos, barlines).
    ///     parts (list[MnxPart]): One or more instrument parts. Every part
    ///         must contain the same number of measures as ``global_data``.
    ///
    /// Returns:
    ///     MnxDocument
    #[new]
    pub fn new(mnx: MnxMetadata, global_data: MnxGlobalData, parts: Vec<MnxPart>) -> PyResult<Self> {
        let global_len = global_data.measures.len();
        for (i, part) in parts.iter().enumerate() {
            if part.measures.len() != global_len {
                return Err(PyValueError::new_err(format!(
                    "part {} has {} measures but global data has {}",
                    i,
                    part.measures.len(),
                    global_len
                )));
            }
        }
        Ok(Self { mnx, global_data, parts })
    }

    /// The MNX metadata (version, etc.).
    #[getter]
    fn mnx(&self) -> MnxMetadata {
        self.mnx.clone()
    }

    /// The global measure data.
    #[getter]
    fn global_data(&self) -> MnxGlobalData {
        self.global_data.clone()
    }

    /// The instrument parts.
    #[getter]
    fn parts(&self) -> Vec<MnxPart> {
        self.parts.clone()
    }

    /// Serialize this document to a compact MNX JSON string.
    ///
    /// Returns:
    ///     str: A compact JSON representation of this MNX document.
    fn to_json(&self) -> PyResult<String> {
        serde_json::to_string(self)
            .map_err(|e| PyValueError::new_err(format!("JSON serialization error: {e}")))
    }

    /// Serialize this document to a pretty-printed MNX JSON string.
    ///
    /// Returns:
    ///     str: An indented JSON representation of this MNX document.
    fn to_json_pretty(&self) -> PyResult<String> {
        serde_json::to_string_pretty(self)
            .map_err(|e| PyValueError::new_err(format!("JSON serialization error: {e}")))
    }

    /// Parse an MNX JSON string into an :class:`MnxDocument`.
    ///
    /// Args:
    ///     json (str): A valid MNX JSON string.
    ///
    /// Returns:
    ///     MnxDocument
    ///
    /// Raises:
    ///     ValueError: If the JSON is malformed or does not match the MNX schema.
    #[staticmethod]
    fn from_json(json: &str) -> PyResult<Self> {
        serde_json::from_str(json)
            .map_err(|e| PyValueError::new_err(format!("JSON parse error: {e}")))
    }
}
