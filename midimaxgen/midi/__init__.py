"""
MIDI output module for MidiMaxGen.

This module provides MIDI file writing capabilities using the mido library.

Classes:
    MidiWriter: Creates and writes MIDI files with notes and chords

Example:
    >>> from midimaxgen.midi import MidiWriter
    >>> writer = MidiWriter(bpm=120)
    >>> writer.add_note('C4', duration_beats=1.0)
    >>> writer.add_note('E4', duration_beats=1.0)
    >>> writer.save('output.mid')
"""

from midimaxgen.midi.writer import MidiWriter

__all__ = ["MidiWriter"]