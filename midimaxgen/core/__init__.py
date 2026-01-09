"""
Core music theory components for MidiMaxGen.

This module provides foundational classes for representing musical concepts:
- Note: Individual musical notes with pitch and octave
- Chord: Collections of notes with defined intervals
- Scale: Musical scales and key signatures
"""

from midimaxgen.core.note import Note, NOTE_NAMES
from midimaxgen.core.chord import Chord, CHORD_TYPES
from midimaxgen.core.scale import Scale, MAJOR_SCALE, SCALE_DEGREE_CHORD_TYPES

__all__ = [
    "Note",
    "NOTE_NAMES",
    "Chord", 
    "CHORD_TYPES",
    "Scale",
    "MAJOR_SCALE",
    "SCALE_DEGREE_CHORD_TYPES",
]