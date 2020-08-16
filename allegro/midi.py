import dataclasses
import logging
import random
import time
from typing import List

import rtmidi
from rtmidi.midiutil import open_midioutput
from rtmidi.midiconstants import NOTE_ON, NOTE_OFF

log = logging.getLogger("allegro.midi")
logging.basicConfig(level=logging.DEBUG)


@dataclasses.dataclass
class MidiPort:
    """
    MidiPort represents a MIDI port.

    port_id -- int
    port_name -- str
    """

    port_id: int
    port_name: str


def get_output_ports() -> List[MidiPort]:
    """
    get_available_ports returns all available midi output ports.

    This returns a list of MidiPort objects.
    """
    ports = rtmidi.MidiOut().get_ports()
    port_ids_and_names = [
        MidiPort(port_id=port_id, port_name=name) for port_id, name in enumerate(ports)
    ]
    log.debug(port_ids_and_names)
    return port_ids_and_names


class MidiOut:
    """
    MidiOut opens a MIDI output connection.

    Methods:
    play -- plays a midi note with given velocity and duration.
    test -- writes a random compositon and sends it to the initialized output.
    """

    def __init__(self, port_id: int):
        self.port_id = port_id
        self.output = self._open_output()

    def _open_output(self) -> rtmidi.MidiOut:
        """
        open_output opens a midi port for output.
        """
        if not self.port_id:
            err_text = "Cannot open output without port selected."
            log.error(err_text)
            raise RuntimeError(err_text)

        midiout, _ = open_midioutput(self.port_id)
        return midiout

    def play(self, note: int, vel: int, dur: float):
        self.output.send_message([NOTE_ON, note, vel])
        time.sleep(dur)
        self.output.send_message([NOTE_OFF, note, 0])

    def _random_event(self):
        note = random.choice(range(30, 90))
        dur = random.choice([0.1, 0.2, 0.5])
        vel = random.choice([128, 100, 80, 60])
        return note, dur, vel

    def test(self):
        """
        test writes a random compositon and sends it to
        the initialized output.

        test will log an error and raise an exception if there
        is not an open output available.
        """
        if not self.output:
            err_text = "Cannot test without open output."
            log.error(err_text)
            raise RuntimeError(err_text)

        for _ in range(10):
            note, dur, vel = self._random_event()
            self.play(note, vel, dur)


def keynum_to_notename(keynum: int) -> str:
    """
    keynum_to_notename takes a MIDI keynumber and converts it
    to a notename.

    args: keynum: int

    returns: str
    """
    log.debug(f"received {keynum}")
    notenames = [
        "C",
        "Db",
        "D",
        "Eb",
        "E",
        "F",
        "Gb",
        "G",
        "Ab",
        "A",
        "Bb",
        "B",
    ]

    notename = notenames[keynum % 12]
    octave = (keynum // 12) - 1  # 60 is C4 aka middle C
    result = notename + str(octave)

    log.debug(f"result: {result}")
    return result

