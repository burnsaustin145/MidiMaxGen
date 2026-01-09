"""
Chord representation for MidiMaxGen.

This module provides the Chord class for representing musical chords,
including common chord types (triads, seventh chords) and their intervals.

Chord Types:
    Triads:
        - major: Root, Major 3rd, Perfect 5th (0, 4, 7)
        - minor: Root, Minor 3rd, Perfect 5th (0, 3, 7)
        - diminished: Root, Minor 3rd, Diminished 5th (0, 3, 6)
        - augmented: Root, Major 3rd, Augmented 5th (0, 4, 8)
    
    Seventh Chords:
        - major7: Major triad + Major 7th (0, 4, 7, 11)
        - minor7: Minor triad + Minor 7th (0, 3, 7, 10)
        - dominant7: Major triad + Minor 7th (0, 4, 7, 10)
        - diminished7: Diminished triad + Diminished 7th (0, 3, 6, 9)
        - half_diminished7: Diminished triad + Minor 7th (0, 3, 6, 10)

Example:
    >>> chord = Chord('C', 'major', octave=4)
    >>> chord.notes
    [Note('C', 4), Note('E', 4), Note('G', 4)]
"""

from typing import List, Optional
from midimaxgen.core.note import Note, NOTE_NAMES, SEMITONE_TO_NAME


# Chord type definitions as intervals from root (in semitones)
# Each list represents the intervals that make up the chord
CHORD_TYPES = {
    # Triads (3 notes)
    'major': [0, 4, 7],          # Root, Major 3rd, Perfect 5th
    'minor': [0, 3, 7],          # Root, Minor 3rd, Perfect 5th
    'diminished': [0, 3, 6],     # Root, Minor 3rd, Diminished 5th
    'augmented': [0, 4, 8],      # Root, Major 3rd, Augmented 5th
    
    # Seventh Chords (4 notes)
    'major7': [0, 4, 7, 11],         # Major triad + Major 7th
    'minor7': [0, 3, 7, 10],         # Minor triad + Minor 7th
    'dominant7': [0, 4, 7, 10],      # Major triad + Minor 7th (V7)
    'diminished7': [0, 3, 6, 9],     # Diminished triad + Diminished 7th
    'half_diminished7': [0, 3, 6, 10],  # Diminished triad + Minor 7th (ø7)
    
    # Suspended Chords
    'sus2': [0, 2, 7],           # Root, Major 2nd, Perfect 5th
    'sus4': [0, 5, 7],           # Root, Perfect 4th, Perfect 5th
    
    # Extended Chords (simplified - just adding the extension)
    'add9': [0, 4, 7, 14],       # Major triad + 9th
    'minor_add9': [0, 3, 7, 14], # Minor triad + 9th
}


class Chord:
    """
    Represents a musical chord built from a root note and chord type.
    
    A Chord is a collection of Notes defined by:
    - A root note (the foundation of the chord)
    - A chord type (defines the intervals between notes)
    - An octave (where the root note sits)
    
    Attributes:
        root (str): The root note name (e.g., 'C', 'F#')
        chord_type (str): The type of chord (e.g., 'major', 'minor7')
        octave (int): The octave of the root note
        notes (List[Note]): The individual notes that make up the chord
    
    Example:
        >>> c_major = Chord('C', 'major', octave=4)
        >>> print(c_major)
        Cmajor
        >>> c_major.note_names
        ['C4', 'E4', 'G4']
        
        >>> g7 = Chord('G', 'dominant7', octave=3)
        >>> g7.note_names
        ['G3', 'B3', 'D4', 'F4']
    """
    
    def __init__(self, root: str, chord_type: str = 'major', octave: int = 4):
        """
        Initialize a Chord with root note, type, and octave.
        
        Args:
            root: Root note name (e.g., 'C', 'F#', 'Bb'). Case-insensitive.
            chord_type: Type of chord from CHORD_TYPES. Default is 'major'.
            octave: Octave for the root note. Default is 4 (middle octave).
        
        Raises:
            ValueError: If root note or chord_type is invalid.
        """
        self.root = root.lower()
        
        if self.root not in NOTE_NAMES:
            raise ValueError(
                f"Invalid root note: '{root}'. "
                f"Valid notes: {list(NOTE_NAMES.keys())}"
            )
        
        if chord_type not in CHORD_TYPES:
            raise ValueError(
                f"Invalid chord type: '{chord_type}'. "
                f"Valid types: {list(CHORD_TYPES.keys())}"
            )
        
        self.chord_type = chord_type
        self.octave = octave
        self._notes = self._build_notes()
    
    def _build_notes(self) -> List[Note]:
        """
        Build the list of notes for this chord based on intervals.
        
        Returns:
            List of Note objects comprising the chord.
        """
        intervals = CHORD_TYPES[self.chord_type]
        root_note = Note(self.root, self.octave)
        
        notes = []
        for interval in intervals:
            # Transpose the root by the interval to get each chord tone
            notes.append(root_note.transpose(interval))
        
        return notes
    
    @property
    def notes(self) -> List[Note]:
        """Get the list of Note objects in this chord."""
        return self._notes.copy()
    
    @property
    def note_names(self) -> List[str]:
        """
        Get list of note names with octaves (e.g., ['C4', 'E4', 'G4']).
        
        Useful for display or passing to MIDI generation functions.
        """
        return [note.name for note in self._notes]
    
    @property
    def midi_numbers(self) -> List[int]:
        """Get list of MIDI note numbers for the chord."""
        return [note.midi_number for note in self._notes]
    
    @property
    def intervals(self) -> List[int]:
        """Get the intervals (in semitones) that define this chord type."""
        return CHORD_TYPES[self.chord_type].copy()
    
    @property
    def size(self) -> int:
        """Get the number of notes in the chord."""
        return len(self._notes)
    
    @classmethod
    def from_notes(cls, notes: List[Note], name: str = 'custom') -> 'Chord':
        """
        Create a Chord from a list of Note objects.
        
        Note: This creates a chord-like object but won't have a standard
        chord_type unless the intervals match a known type.
        
        Args:
            notes: List of Note objects to form the chord.
            name: Optional name for the chord.
        
        Returns:
            Chord instance with the given notes.
        """
        if not notes:
            raise ValueError("Cannot create chord from empty note list")
        
        # Create chord with root as the lowest note
        chord = cls.__new__(cls)
        chord.root = notes[0].pitch
        chord.octave = notes[0].octave
        chord.chord_type = name
        chord._notes = notes
        
        return chord
    
    def invert(self, inversion: int = 1) -> 'Chord':
        """
        Create an inversion of this chord.
        
        Inversions move the lowest note(s) up an octave:
        - 1st inversion: Move root up an octave
        - 2nd inversion: Move root and 3rd up an octave
        - etc.
        
        Args:
            inversion: Which inversion (1, 2, etc.)
        
        Returns:
            New Chord object with the inversion applied.
        
        Example:
            >>> c_major = Chord('C', 'major', 4)
            >>> c_major.note_names
            ['C4', 'E4', 'G4']
            >>> c_major.invert(1).note_names
            ['E4', 'G4', 'C5']
        """
        if inversion <= 0:
            return Chord(self.root, self.chord_type, self.octave)
        
        # Get current notes and rotate them
        notes = self._notes.copy()
        
        for _ in range(min(inversion, len(notes) - 1)):
            # Move the lowest note up an octave
            lowest = notes.pop(0)
            notes.append(lowest.transpose(12))
        
        return Chord.from_notes(notes, f"{self.chord_type}_inv{inversion}")
    
    def transpose(self, semitones: int) -> 'Chord':
        """
        Create a new Chord transposed by the given semitones.
        
        Args:
            semitones: Number of semitones to transpose (positive = up)
        
        Returns:
            New Chord at the transposed pitch.
        
        Example:
            >>> c_major = Chord('C', 'major', 4)
            >>> c_major.transpose(2).root  # D major
            'd'
        """
        # Transpose the root note and create new chord
        root_note = Note(self.root, self.octave)
        new_root = root_note.transpose(semitones)
        
        return Chord(new_root.pitch, self.chord_type, new_root.octave)
    
    def __repr__(self) -> str:
        return f"Chord('{self.root}', '{self.chord_type}', {self.octave})"
    
    def __str__(self) -> str:
        # Format: Cmajor, F#minor7, Bbdominant7, etc.
        display_root = self.root.upper() if len(self.root) == 1 else \
                      self.root[0].upper() + self.root[1]
        return f"{display_root}{self.chord_type}"
    
    def __len__(self) -> int:
        return len(self._notes)
    
    def __iter__(self):
        return iter(self._notes)
    
    def __getitem__(self, index: int) -> Note:
        return self._notes[index]