"""
Note representation for MidiMaxGen.

This module provides the Note class for representing individual musical notes,
including pitch name, octave, and conversion to/from MIDI note numbers.

MIDI Note Numbers:
    - Middle C (C4) = 60
    - Each octave spans 12 semitones
    - Valid range: 0-127 (C-1 to G9)

Example:
    >>> note = Note('C', 4)
    >>> note.midi_number
    60
    >>> note.name
    'C4'
"""

from typing import Optional, Union


# Mapping of note names to semitone values (0-11)
# Includes both sharp (#) and flat (b) enharmonic equivalents
NOTE_NAMES = {
    'c': 0, 'c#': 1, 'db': 1,
    'd': 2, 'd#': 3, 'eb': 3,
    'e': 4,
    'f': 5, 'f#': 6, 'gb': 6,
    'g': 7, 'g#': 8, 'ab': 8,
    'a': 9, 'a#': 10, 'bb': 10,
    'b': 11
}

# Reverse mapping: semitone value to preferred note name (sharps preferred)
SEMITONE_TO_NAME = {
    0: 'C', 1: 'C#', 2: 'D', 3: 'D#', 4: 'E', 5: 'F',
    6: 'F#', 7: 'G', 8: 'G#', 9: 'A', 10: 'A#', 11: 'B'
}


class Note:
    """
    Represents a single musical note with pitch and octave.
    
    A Note combines a pitch class (C, D, E, etc.) with an octave number
    to specify an exact frequency/MIDI note number.
    
    Attributes:
        pitch (str): The pitch class name (e.g., 'C', 'F#', 'Bb')
        octave (int): The octave number (typically 0-9)
        midi_number (int): The MIDI note number (0-127)
    
    Example:
        >>> middle_c = Note('C', 4)
        >>> print(middle_c)
        C4
        >>> middle_c.midi_number
        60
        
        >>> Note.from_midi(60)
        Note('C', 4)
    """
    
    def __init__(self, pitch: str, octave: int):
        """
        Initialize a Note with pitch and octave.
        
        Args:
            pitch: Note name (e.g., 'C', 'F#', 'Bb'). Case-insensitive.
            octave: Octave number. Middle C is in octave 4.
        
        Raises:
            ValueError: If pitch name is invalid or octave is out of range.
        """
        self.pitch = pitch.lower()
        
        if self.pitch not in NOTE_NAMES:
            raise ValueError(
                f"Invalid pitch name: '{pitch}'. "
                f"Valid names: {list(NOTE_NAMES.keys())}"
            )
        
        self.octave = octave
        self._midi_number = self._calculate_midi_number()
        
        # Validate MIDI number is in valid range
        if not 0 <= self._midi_number <= 127:
            raise ValueError(
                f"Note {pitch}{octave} results in MIDI number {self._midi_number}, "
                f"which is outside valid range 0-127"
            )
    
    def _calculate_midi_number(self) -> int:
        """Calculate MIDI note number from pitch and octave."""
        # MIDI standard: C4 = 60, each octave = 12 semitones
        # Formula: (octave + 1) * 12 + semitone_value
        return (self.octave + 1) * 12 + NOTE_NAMES[self.pitch]
    
    @property
    def midi_number(self) -> int:
        """Get the MIDI note number (0-127)."""
        return self._midi_number
    
    @property
    def name(self) -> str:
        """Get the full note name with octave (e.g., 'C4', 'F#5')."""
        # Use uppercase for display
        display_pitch = self.pitch.upper() if len(self.pitch) == 1 else \
                       self.pitch[0].upper() + self.pitch[1]
        return f"{display_pitch}{self.octave}"
    
    @property
    def semitone(self) -> int:
        """Get the semitone value (0-11) within the octave."""
        return NOTE_NAMES[self.pitch]
    
    @classmethod
    def from_midi(cls, midi_number: int) -> 'Note':
        """
        Create a Note from a MIDI note number.
        
        Args:
            midi_number: MIDI note number (0-127)
        
        Returns:
            Note instance corresponding to the MIDI number.
        
        Raises:
            ValueError: If midi_number is outside valid range.
        
        Example:
            >>> Note.from_midi(60)
            Note('C', 4)
        """
        if not 0 <= midi_number <= 127:
            raise ValueError(f"MIDI number must be 0-127, got {midi_number}")
        
        octave = (midi_number // 12) - 1
        semitone = midi_number % 12
        pitch = SEMITONE_TO_NAME[semitone]
        
        return cls(pitch, octave)
    
    @classmethod
    def from_string(cls, note_string: str) -> 'Note':
        """
        Parse a note from string format (e.g., 'C4', 'F#5', 'Bb3').
        
        Args:
            note_string: Note in format like 'C4', 'F#5', 'Bb3'
        
        Returns:
            Note instance.
        
        Raises:
            ValueError: If string format is invalid.
        
        Example:
            >>> Note.from_string('C4')
            Note('C', 4)
            >>> Note.from_string('F#5')
            Note('F#', 5)
        """
        if not note_string or len(note_string) < 2:
            raise ValueError(f"Invalid note string: '{note_string}'")
        
        # Handle sharps and flats (2 char pitch) vs natural notes (1 char pitch)
        if len(note_string) >= 3 and note_string[1] in '#b':
            pitch = note_string[:2]
            octave_str = note_string[2:]
        else:
            pitch = note_string[0]
            octave_str = note_string[1:]
        
        try:
            octave = int(octave_str)
        except ValueError:
            raise ValueError(f"Invalid octave in note string: '{note_string}'")
        
        return cls(pitch, octave)
    
    def transpose(self, semitones: int) -> 'Note':
        """
        Create a new Note transposed by the given number of semitones.
        
        Args:
            semitones: Number of semitones to transpose (positive = up, negative = down)
        
        Returns:
            New Note instance at the transposed pitch.
        
        Example:
            >>> c4 = Note('C', 4)
            >>> c4.transpose(2)  # Up a whole step
            Note('D', 4)
            >>> c4.transpose(12)  # Up an octave
            Note('C', 5)
        """
        new_midi = self._midi_number + semitones
        return Note.from_midi(new_midi)
    
    def __repr__(self) -> str:
        return f"Note('{self.pitch}', {self.octave})"
    
    def __str__(self) -> str:
        return self.name
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Note):
            return self._midi_number == other._midi_number
        return False
    
    def __hash__(self) -> int:
        return hash(self._midi_number)
    
    def __lt__(self, other: 'Note') -> bool:
        return self._midi_number < other._midi_number