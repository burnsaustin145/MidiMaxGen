"""
Main Arpeggiator class for MidiMaxGen.

This module provides the high-level Arpeggiator class that combines all components
(scales, chords, patterns, MIDI output) into an easy-to-use interface for generating
MIDI arpeggios.

The Arpeggiator is the main entry point for most users of the library. It handles:
- Converting chord progressions (scale degrees) to actual notes
- Applying arpeggio patterns to chord notes
- Writing the result to MIDI files

Example:
    >>> from midimaxgen import Arpeggiator
    >>> 
    >>> # Create an arpeggiator in C major
    >>> arp = Arpeggiator(key='C', octave=4, bpm=120)
    >>> 
    >>> # Generate a I-V-vi-IV progression with 'up' pattern
    >>> arp.generate_arpeggio(
    ...     progression=[1, 5, 6, 4],
    ...     durations=[1, 1, 1, 1],
    ...     pattern='up',
    ...     notes_per_chord=8
    ... )
    >>> 
    >>> # Save to MIDI file
    >>> arp.save('my_arpeggio.mid')
"""

from typing import List, Optional, Union, Dict, Any

from midimaxgen.core.scale import Scale, SCALE_DEGREE_CHORD_TYPES
from midimaxgen.core.chord import Chord, CHORD_TYPES
from midimaxgen.core.note import Note
from midimaxgen.midi.writer import MidiWriter
from midimaxgen.patterns.simple import SimplePattern, SIMPLE_PATTERN_TYPES
from midimaxgen.patterns.group import GroupPattern, generate_permutation_sequences


# All available pattern types (simple + group)
AVAILABLE_PATTERNS = list(SIMPLE_PATTERN_TYPES.keys()) + ['group']


class Arpeggiator:
    """
    High-level arpeggio generator combining scales, patterns, and MIDI output.
    
    The Arpeggiator provides a simple interface for generating MIDI arpeggios
    from chord progressions specified as scale degrees. It handles:
    
    1. Converting scale degrees to chords based on the key
    2. Applying arpeggio patterns to determine note order
    3. Writing the resulting notes to a MIDI file
    
    Attributes:
        key (str): The musical key (e.g., 'C', 'G', 'F#')
        octave (int): Base octave for the arpeggios
        bpm (int): Tempo in beats per minute
        program (int): MIDI program number (instrument)
        scale (Scale): The Scale object for the current key
    
    Supported Patterns:
        Simple patterns:
            - 'up': Ascending arpeggio (C-E-G-C-E-G...)
            - 'down': Descending arpeggio (G-E-C-G-E-C...)
            - 'up_down': Ping-pong arpeggio (C-E-G-E-C-E-G-E...)
        
        Group theory patterns:
            - 'group': Uses permutations from symmetric groups
                      Supports 'lex', 'random', 'conjugacy', 'coset' orderings
    
    Example:
        Basic usage with simple patterns:
        
        >>> arp = Arpeggiator(key='C', octave=4, bpm=120)
        >>> arp.generate_arpeggio(
        ...     progression=[1, 5, 6, 4],  # I-V-vi-IV
        ...     durations=[1, 1, 1, 1],
        ...     pattern='up',
        ...     notes_per_chord=8
        ... )
        >>> arp.save('pop_progression.mid')
        
        Advanced usage with group patterns:
        
        >>> arp = Arpeggiator(key='A', octave=3, bpm=90)
        >>> arp.generate_arpeggio(
        ...     progression=[6, 4, 1, 5],  # vi-IV-I-V
        ...     durations=[2, 2, 2, 2],
        ...     pattern='group',
        ...     order='conjugacy'  # Group theory ordering
        ... )
        >>> arp.save('math_arpeggio.mid')
    """
    
    def __init__(
        self, 
        key: str = 'c', 
        octave: int = 4, 
        bpm: int = 120, 
        program: int = 0
    ):
        """
        Initialize the Arpeggiator with musical and MIDI settings.
        
        Args:
            key: The musical key for the arpeggio (e.g., 'C', 'G', 'F#', 'Bb').
                 Case-insensitive. Default is 'C'.
            octave: Base octave for chord notes. Default is 4 (middle octave).
            bpm: Tempo in beats per minute. Default is 120.
            program: MIDI program number (0-127) for instrument selection.
                    Default is 0 (Acoustic Grand Piano).
        
        Raises:
            ValueError: If key is not a valid note name.
        
        Example:
            >>> arp = Arpeggiator(key='G', octave=4, bpm=140, program=4)
        """
        # Create the MIDI writer
        self.midi_writer = MidiWriter(bpm=bpm, program=program)
        
        # Store settings
        self.key = key.lower()
        self.octave = octave
        self.bpm = bpm
        self.program = program
        
        # Create the scale for this key
        self.scale = Scale(key, 'major', octave)
        
        # Track the current beat position for sequential note adding
        self.current_beat = 0
    
    def degree_to_notes(
        self, 
        degree: int, 
        chord_type: Optional[str] = None,
        octave: Optional[int] = None
    ) -> List[str]:
        """
        Convert a scale degree to a list of note names for the chord.
        
        This method uses diatonic harmony rules to determine the chord type
        for each scale degree (unless overridden).
        
        Args:
            degree: Scale degree (1-7). 1=tonic, 5=dominant, etc.
            chord_type: Override the default chord type (e.g., 'major', 'minor7').
                       If None, uses diatonic chord type for the degree.
            octave: Override the base octave for the chord.
        
        Returns:
            List of note name strings (e.g., ['C4', 'E4', 'G4'])
        
        Example:
            >>> arp = Arpeggiator(key='C')
            >>> arp.degree_to_notes(1)  # I chord in C
            ['C4', 'E4', 'G4']
            >>> arp.degree_to_notes(2)  # ii chord in C
            ['D4', 'F4', 'A4']
            >>> arp.degree_to_notes(5, chord_type='dominant7')  # V7
            ['G4', 'B4', 'D5', 'F5']
        """
        if octave is None:
            octave = self.octave
        
        # Get the chord from the scale
        chord = self.scale.degree_to_chord(
            degree, 
            chord_type=chord_type, 
            octave=octave
        )
        
        return chord.note_names
    
    def generate_arpeggio(
        self,
        progression: List[int],
        durations: List[float],
        notes_per_chord: int = 8,
        pattern: str = 'up',
        note_duration: float = 0.25,
        velocity: int = 64,
        spacing_factor: float = 1.0,
        order: str = 'conjugacy',
        subgroup: Optional[List] = None,
        permutation_size: Optional[int] = None
    ) -> None:
        """
        Generate an arpeggio sequence based on a chord progression.
        
        This method creates an arpeggio by:
        1. Converting each scale degree to chord notes
        2. Applying the specified pattern to order the notes
        3. Adding the notes to the MIDI file with specified timing
        
        Args:
            progression: List of scale degrees (1-7) representing the chord
                        progression. Example: [1, 5, 6, 4] for I-V-vi-IV
            durations: List of durations for each chord in beats. Must be
                      same length as progression.
            notes_per_chord: Number of arpeggio notes per chord for simple
                           patterns. Default is 8.
            pattern: Arpeggio pattern type:
                    - 'up': Ascending
                    - 'down': Descending  
                    - 'up_down': Ping-pong
                    - 'group': Group theory based
            note_duration: Duration of each individual note in beats.
                          Default is 0.25 (sixteenth note at standard tempo).
            velocity: MIDI velocity (volume) 0-127. Default is 64.
            spacing_factor: Multiplier for time between notes. Default is 1.0.
            order: For 'group' pattern, the permutation ordering:
                  'lex', 'random', 'conjugacy', or 'coset'
            subgroup: For 'coset' ordering, the subgroup generators.
            permutation_size: For 'group' pattern, size of permutation group.
                            Defaults to 8 if not specified.
        
        Raises:
            ValueError: If progression and durations have different lengths,
                       or if pattern type is unknown.
        
        Example:
            >>> arp = Arpeggiator(key='C', octave=4, bpm=120)
            >>> 
            >>> # Simple ascending arpeggio
            >>> arp.generate_arpeggio(
            ...     progression=[1, 4, 5, 1],
            ...     durations=[1, 1, 1, 1],
            ...     pattern='up',
            ...     notes_per_chord=4
            ... )
            >>> 
            >>> # Group theory pattern
            >>> arp.generate_arpeggio(
            ...     progression=[6, 4, 1, 5],
            ...     durations=[2, 2, 2, 2],
            ...     pattern='group',
            ...     order='conjugacy'
            ... )
        """
        # Validate inputs
        if len(progression) != len(durations):
            raise ValueError(
                f"Progression length ({len(progression)}) must match "
                f"durations length ({len(durations)})"
            )
        
        if pattern not in AVAILABLE_PATTERNS:
            raise ValueError(
                f"Unknown pattern: '{pattern}'. "
                f"Available patterns: {AVAILABLE_PATTERNS}"
            )
        
        # Generate the arpeggio notes based on pattern type
        if pattern == 'group':
            # Use group theory pattern
            arpeggio_notes = self._generate_group_pattern(
                progression=progression,
                order=order,
                subgroup=subgroup,
                permutation_size=permutation_size or 8
            )
        else:
            # Use simple pattern
            arpeggio_notes = self._generate_simple_pattern(
                progression=progression,
                durations=durations,
                pattern=pattern,
                notes_per_chord=notes_per_chord
            )
        
        # Add notes to MIDI file
        for note in arpeggio_notes:
            self.midi_writer.add_note(
                note,
                velocity=velocity,
                duration_beats=note_duration
            )
    
    def _generate_simple_pattern(
        self,
        progression: List[int],
        durations: List[float],
        pattern: str,
        notes_per_chord: int
    ) -> List[str]:
        """
        Generate notes using a simple arpeggio pattern.
        
        Args:
            progression: List of scale degrees
            durations: Duration of each chord
            pattern: Pattern type ('up', 'down', 'up_down')
            notes_per_chord: Notes to generate per chord
        
        Returns:
            List of note name strings
        """
        simple_pattern = SimplePattern(pattern)
        all_notes = []
        
        for degree in progression:
            # Get chord notes for this degree
            chord_notes = self.degree_to_notes(degree)
            
            # Apply pattern
            pattern_notes = simple_pattern.generate(chord_notes, notes_per_chord)
            all_notes.extend(pattern_notes)
        
        return all_notes
    
    def _generate_group_pattern(
        self,
        progression: List[int],
        order: str,
        subgroup: Optional[List],
        permutation_size: int
    ) -> List[str]:
        """
        Generate notes using group theory permutation patterns.
        
        Each permutation is applied to reorder chord notes. The permutations
        cycle through the chord progression.
        
        Args:
            progression: List of scale degrees
            order: Permutation ordering type
            subgroup: Subgroup for coset ordering
            permutation_size: Size of permutation group S_n
        
        Returns:
            List of note name strings
        """
        # Generate permutations
        perms = generate_permutation_sequences(
            n=permutation_size,
            order=order,
            subgroup=subgroup
        )
        
        if not perms:
            # Fallback: use identity permutation
            perms = [tuple(range(1, permutation_size + 1))]
        
        all_notes = []
        
        for i, perm in enumerate(perms):
            # Select chord (cycle through progression)
            degree = progression[i % len(progression)]
            chord_notes = self.degree_to_notes(degree)
            
            # Apply permutation to chord notes
            # Convert 1-based permutation indices to 0-based
            for p in perm:
                idx = (p - 1) % len(chord_notes)
                all_notes.append(chord_notes[idx])
        
        return all_notes
    
    def add_note(
        self,
        note: Union[str, Note],
        velocity: int = 64,
        duration_beats: float = 1.0
    ) -> None:
        """
        Add a single note directly to the MIDI output.
        
        This is a lower-level method for direct note control.
        
        Args:
            note: Note to add (string like 'C4' or Note object)
            velocity: MIDI velocity (0-127)
            duration_beats: Duration in beats
        """
        self.midi_writer.add_note(note, velocity, duration_beats)
    
    def add_chord(
        self,
        notes: List[Union[str, Note]],
        velocity: int = 64,
        duration_beats: float = 1.0
    ) -> None:
        """
        Add a chord directly to the MIDI output.
        
        Args:
            notes: List of notes to play simultaneously
            velocity: MIDI velocity (0-127)
            duration_beats: Duration in beats
        """
        note_strings = [
            n if isinstance(n, str) else n.name 
            for n in notes
        ]
        self.midi_writer.add_chord(note_strings, velocity, duration_beats)
    
    def save(self, filename: str) -> None:
        """
        Save the generated MIDI to a file.
        
        Args:
            filename: Output filename (should end in .mid or .midi)
        
        Example:
            >>> arp = Arpeggiator()
            >>> arp.generate_arpeggio([1, 4, 5, 1], [1, 1, 1, 1])
            >>> arp.save('my_arpeggio.mid')
        """
        self.midi_writer.save(filename)
    
    def reset(self) -> None:
        """
        Reset the arpeggiator to start fresh.
        
        Clears all previously added notes while keeping settings.
        """
        self.midi_writer.reset()
        self.current_beat = 0
    
    @classmethod
    def available_patterns(cls) -> List[str]:
        """
        Get list of available arpeggio patterns.
        
        Returns:
            List of pattern names
        """
        return AVAILABLE_PATTERNS.copy()
    
    def __repr__(self) -> str:
        return (
            f"Arpeggiator(key='{self.key}', octave={self.octave}, "
            f"bpm={self.bpm}, program={self.program})"
        )