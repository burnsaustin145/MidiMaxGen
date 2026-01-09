"""
Scale and key representation for MidiMaxGen.

This module provides the Scale class for representing musical scales and keys,
including the relationship between scale degrees and chord types in diatonic harmony.

Scale Degrees (in Major Keys):
    1 (I)   - Tonic: Major chord
    2 (ii)  - Supertonic: Minor chord
    3 (iii) - Mediant: Minor chord
    4 (IV)  - Subdominant: Major chord
    5 (V)   - Dominant: Major chord (often dominant7)
    6 (vi)  - Submediant: Minor chord
    7 (vii°)- Leading tone: Diminished chord

Example:
    >>> scale = Scale('C', 'major')
    >>> scale.degree_to_chord(5)  # V chord in C major
    Chord('G', 'major', 4)
"""

from typing import List, Optional, Dict, Tuple
from midimaxgen.core.note import Note, NOTE_NAMES, SEMITONE_TO_NAME
from midimaxgen.core.chord import Chord, CHORD_TYPES


# Major scale intervals (semitones from root)
# W-W-H-W-W-W-H pattern (Whole, Whole, Half, Whole, Whole, Whole, Half)
MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]

# Natural minor scale intervals
# W-H-W-W-H-W-W pattern
NATURAL_MINOR_SCALE = [0, 2, 3, 5, 7, 8, 10]

# Harmonic minor scale intervals (raised 7th)
HARMONIC_MINOR_SCALE = [0, 2, 3, 5, 7, 8, 11]

# Melodic minor scale intervals (ascending - raised 6th and 7th)
MELODIC_MINOR_SCALE = [0, 2, 3, 5, 7, 9, 11]

# Available scale types and their intervals
SCALE_TYPES = {
    'major': MAJOR_SCALE,
    'natural_minor': NATURAL_MINOR_SCALE,
    'harmonic_minor': HARMONIC_MINOR_SCALE,
    'melodic_minor': MELODIC_MINOR_SCALE,
    'ionian': MAJOR_SCALE,           # Mode 1 (same as major)
    'dorian': [0, 2, 3, 5, 7, 9, 10],    # Mode 2
    'phrygian': [0, 1, 3, 5, 7, 8, 10],  # Mode 3
    'lydian': [0, 2, 4, 6, 7, 9, 11],    # Mode 4
    'mixolydian': [0, 2, 4, 5, 7, 9, 10], # Mode 5
    'aeolian': NATURAL_MINOR_SCALE,       # Mode 6 (same as natural minor)
    'locrian': [0, 1, 3, 5, 6, 8, 10],    # Mode 7
    'pentatonic_major': [0, 2, 4, 7, 9],
    'pentatonic_minor': [0, 3, 5, 7, 10],
    'blues': [0, 3, 5, 6, 7, 10],
}

# Chord types for each scale degree in major keys
# These follow standard diatonic harmony rules
SCALE_DEGREE_CHORD_TYPES = {
    1: 'major',      # I chord (Tonic)
    2: 'minor',      # ii chord (Supertonic)
    3: 'minor',      # iii chord (Mediant)
    4: 'major',      # IV chord (Subdominant)
    5: 'major',      # V chord (Dominant) - could also be dominant7
    6: 'minor',      # vi chord (Submediant)
    7: 'diminished'  # vii° chord (Leading tone)
}

# Seventh chord versions for each scale degree
SCALE_DEGREE_SEVENTH_TYPES = {
    1: 'major7',         # Imaj7
    2: 'minor7',         # ii7
    3: 'minor7',         # iii7
    4: 'major7',         # IVmaj7
    5: 'dominant7',      # V7
    6: 'minor7',         # vi7
    7: 'half_diminished7'  # viiø7
}


class Scale:
    """
    Represents a musical scale/key with methods for generating chords.
    
    A Scale defines the relationship between notes in a key and provides
    methods for generating chords based on scale degrees (Roman numeral analysis).
    
    Attributes:
        root (str): The root note of the scale (e.g., 'C', 'F#')
        scale_type (str): The type of scale (e.g., 'major', 'natural_minor')
        octave (int): Default octave for generated notes/chords
    
    Example:
        >>> c_major = Scale('C', 'major')
        >>> c_major.get_notes()
        [Note('C', 4), Note('D', 4), Note('E', 4), ...]
        
        >>> c_major.degree_to_chord(1)  # I chord
        Chord('C', 'major', 4)
        
        >>> c_major.degree_to_chord(5, seventh=True)  # V7 chord
        Chord('G', 'dominant7', 4)
    """
    
    def __init__(self, root: str, scale_type: str = 'major', octave: int = 4):
        """
        Initialize a Scale with root note, type, and octave.
        
        Args:
            root: Root note of the scale (e.g., 'C', 'G', 'F#'). Case-insensitive.
            scale_type: Type of scale from SCALE_TYPES. Default is 'major'.
            octave: Default octave for generated notes. Default is 4.
        
        Raises:
            ValueError: If root note or scale_type is invalid.
        """
        self.root = root.lower()
        
        if self.root not in NOTE_NAMES:
            raise ValueError(
                f"Invalid root note: '{root}'. "
                f"Valid notes: {list(NOTE_NAMES.keys())}"
            )
        
        if scale_type not in SCALE_TYPES:
            raise ValueError(
                f"Invalid scale type: '{scale_type}'. "
                f"Valid types: {list(SCALE_TYPES.keys())}"
            )
        
        self.scale_type = scale_type
        self.octave = octave
        self._intervals = SCALE_TYPES[scale_type]
    
    @property
    def intervals(self) -> List[int]:
        """Get the intervals (semitones from root) for this scale type."""
        return self._intervals.copy()
    
    @property
    def root_semitone(self) -> int:
        """Get the semitone value (0-11) of the root note."""
        return NOTE_NAMES[self.root]
    
    def get_notes(self, octave: Optional[int] = None) -> List[Note]:
        """
        Get all notes in the scale for a given octave.
        
        Args:
            octave: Octave for the scale. Uses default if not specified.
        
        Returns:
            List of Note objects representing the scale.
        
        Example:
            >>> Scale('C', 'major').get_notes()
            [Note('c', 4), Note('d', 4), Note('e', 4), Note('f', 4), 
             Note('g', 4), Note('a', 4), Note('b', 4)]
        """
        if octave is None:
            octave = self.octave
        
        root_note = Note(self.root, octave)
        return [root_note.transpose(interval) for interval in self._intervals]
    
    def get_note_names(self, octave: Optional[int] = None) -> List[str]:
        """
        Get note names with octaves for all scale notes.
        
        Args:
            octave: Octave for the scale. Uses default if not specified.
        
        Returns:
            List of note name strings (e.g., ['C4', 'D4', 'E4', ...])
        """
        return [note.name for note in self.get_notes(octave)]
    
    def degree_to_note(self, degree: int, octave: Optional[int] = None) -> Note:
        """
        Get the note at a specific scale degree.
        
        Args:
            degree: Scale degree (1-7 for standard scales, wraps for higher)
            octave: Base octave. Uses default if not specified.
        
        Returns:
            Note at the specified scale degree.
        
        Example:
            >>> Scale('C', 'major').degree_to_note(5)  # 5th degree = G
            Note('g', 4)
        """
        if octave is None:
            octave = self.octave
        
        # Normalize degree to 1-based within scale length
        num_degrees = len(self._intervals)
        normalized = ((degree - 1) % num_degrees)
        octave_offset = (degree - 1) // num_degrees
        
        root_note = Note(self.root, octave + octave_offset)
        return root_note.transpose(self._intervals[normalized])
    
    def degree_to_chord(
        self, 
        degree: int, 
        chord_type: Optional[str] = None,
        seventh: bool = False,
        octave: Optional[int] = None
    ) -> Chord:
        """
        Get the diatonic chord for a scale degree.
        
        This method generates the chord that naturally occurs on the given
        scale degree according to diatonic harmony rules.
        
        Args:
            degree: Scale degree (1-7)
            chord_type: Override the default chord type. If None, uses
                       diatonic chord type for this degree.
            seventh: If True, use seventh chord instead of triad.
            octave: Octave for the chord root. Uses default if not specified.
        
        Returns:
            Chord object for the specified scale degree.
        
        Example:
            >>> scale = Scale('C', 'major')
            >>> scale.degree_to_chord(1)  # I chord
            Chord('c', 'major', 4)
            >>> scale.degree_to_chord(2)  # ii chord
            Chord('d', 'minor', 4)
            >>> scale.degree_to_chord(5, seventh=True)  # V7 chord
            Chord('g', 'dominant7', 4)
        """
        if octave is None:
            octave = self.octave
        
        # Normalize degree to 1-7
        normalized_degree = ((degree - 1) % 7) + 1
        
        # Get the root note for this chord
        root_note = self.degree_to_note(degree, octave)
        
        # Determine chord type
        if chord_type is None:
            if seventh:
                chord_type = SCALE_DEGREE_SEVENTH_TYPES.get(
                    normalized_degree, 'major7'
                )
            else:
                chord_type = SCALE_DEGREE_CHORD_TYPES.get(
                    normalized_degree, 'major'
                )
        
        return Chord(root_note.pitch, chord_type, root_note.octave)
    
    def degree_to_note_names(
        self, 
        degree: int, 
        chord_type: Optional[str] = None,
        seventh: bool = False,
        octave: Optional[int] = None
    ) -> List[str]:
        """
        Get chord note names for a scale degree.
        
        Convenience method that returns note name strings instead of a Chord.
        
        Args:
            degree: Scale degree (1-7)
            chord_type: Override chord type (optional)
            seventh: Use seventh chord if True
            octave: Octave for chord root
        
        Returns:
            List of note name strings (e.g., ['C4', 'E4', 'G4'])
        """
        chord = self.degree_to_chord(degree, chord_type, seventh, octave)
        return chord.note_names
    
    def get_progression_chords(
        self, 
        degrees: List[int],
        seventh: bool = False,
        octave: Optional[int] = None
    ) -> List[Chord]:
        """
        Generate a chord progression from scale degrees.
        
        Args:
            degrees: List of scale degrees (e.g., [1, 4, 5, 1] for I-IV-V-I)
            seventh: Use seventh chords if True
            octave: Base octave for chords
        
        Returns:
            List of Chord objects.
        
        Example:
            >>> scale = Scale('C', 'major')
            >>> scale.get_progression_chords([1, 5, 6, 4])  # I-V-vi-IV
            [Chord('c', 'major', 4), Chord('g', 'major', 4), 
             Chord('a', 'minor', 4), Chord('f', 'major', 4)]
        """
        return [
            self.degree_to_chord(degree, seventh=seventh, octave=octave)
            for degree in degrees
        ]
    
    def transpose(self, semitones: int) -> 'Scale':
        """
        Create a new Scale transposed by the given semitones.
        
        Args:
            semitones: Number of semitones to transpose (positive = up)
        
        Returns:
            New Scale at the transposed key.
        
        Example:
            >>> c_major = Scale('C', 'major')
            >>> c_major.transpose(2)  # D major
            Scale('d', 'major', 4)
        """
        root_note = Note(self.root, self.octave)
        new_root = root_note.transpose(semitones)
        return Scale(new_root.pitch, self.scale_type, self.octave)
    
    def __repr__(self) -> str:
        return f"Scale('{self.root}', '{self.scale_type}', {self.octave})"
    
    def __str__(self) -> str:
        display_root = self.root.upper() if len(self.root) == 1 else \
                      self.root[0].upper() + self.root[1]
        return f"{display_root} {self.scale_type}"