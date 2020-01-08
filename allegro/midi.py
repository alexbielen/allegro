import dataclasses
import logging
import random
import time
from typing import List, Optional

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


class MidiOut:
    """
    MidiOut handles midi output related activities.

    Properties:
    midiout -- access to the rtmidi MidiOut object.
    port_id -- an integer representing a midi port.
    output -- after initialization by open_output, output is
    a port that can receive midi messages.


    Methods:
    get_available_ports -- returns all available midi output ports.
    open_output -- opens a midi port for output.
    test -- writes a random compositon and sends it to the initialized output.
    """

    def __init__(self, port_id: int = None):
        self.midiout = rtmidi.MidiOut()
        self._port_id = port_id
        self.output = None
        if port_id:
            log.debug(f"initializing MidiOut with port_id: {port_id}")
            self.open_output(port_id)

    @property
    def port_id(self) -> Optional[int]:
        """
        port_id gets the port_id for the class.
        """
        log.debug(f"getting port_id of value {self._port_id}")
        return self._port_id

    @port_id.setter
    def port_id(self, port_id: int) -> None:
        """
        port_id sets the port_id for the class.
        """
        log.debug(f"setting port to {port_id}")
        self._port_id = port_id

    def get_available_ports(self) -> List[MidiPort]:
        """
        get_available_ports returns all available midi output ports.

        These are returned in a list of tuples in which the port_id is
        the first member of the tuple and the port name is the second.

        Ex: [(0, "Virtual IAC Bus"), (1, "SimpleSynth")]
        """
        ports = self.midiout.get_ports()
        port_ids_and_names = [
            MidiPort(port_id=port_id, port_name=name)
            for port_id, name in enumerate(ports)
        ]
        log.debug(port_ids_and_names)
        return port_ids_and_names

    def open_output(self, port_id=None) -> None:
        """
        open_output opens a midi port for output.

        open_port can take the port_id to be opened as an argument or
        it can use the class's port_id property.

        optional arguments:
        port -- int: the port to open.
        """
        if not self.port_id and not port_id:
            log.error("Cannot open output without port selected.")
            return
        try:
            midiout, _ = open_midioutput(self.port_id)
            self.output = midiout
        except (EOFError, KeyboardInterrupt) as e:
            log.error(f"Could not open port. Hint: Check that valid port is set. {e}")

    def test(self):
        """
        test writes a random compositon and sends it to
        the initialized output.

        test will return early and log an error if there
        is not an open output available.
        """
        if not self.output:
            log.error("Cannot test without open output.")
            return

        def random_event():
            note = random.choice(range(30, 90))
            dur = random.choice([0.1, 0.2, 0.5])
            vel = random.choice([128, 100, 80, 60])
            return note, dur, vel

        for _ in range(10):
            note, dur, vel = random_event()
            self.output.send_message([NOTE_ON, note, vel])
            time.sleep(dur)
            self.output.send_message([NOTE_OFF, note, 0])
