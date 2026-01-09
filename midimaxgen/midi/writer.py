"""
MIDI file writer for MidiMaxGen.

This module provides the MidiWriter class for creating MIDI files with notes,
chords, and configurable parameters like BPM and instrument (program).

MIDI Basics:
    - MIDI note numbers range from 0-127
    - Middle C (C4) = MIDI note 60
    - Each octave spans 12 semitones
    - Timing is measured in "ticks" (typically 480 ticks per quarter note)
    - Velocity (volume) ranges from 0-127

Example:
    >>> writer = MidiWriter(bpm=120, program=0)  # Piano at 120 BPM
    >>> writer.add_note('C4', duration_beats=1.0)
    >>> writer.add_chord(['C4', 'E4', 'G4'], duration_beats=2.0)
    >>> writer.save('output.mid')

Dependencies:
    Requires the mido library: pip install mido
"""

from typing import List, Optional, Union
from mido import MidiFile, MidiTrack, Message

from midimaxgen.core.note import Note, NOTE_NAMES


# Standard MIDI timing: ticks per quarter note (beat)
TICKS_PER_BEAT = 480


class MidiWriter:
    """
    MIDI file writer for creating standard MIDI files.
    
    This class provides methods to create MIDI files by adding individual
    notes or chords. Notes can be specified by name (e.g., 'C4') or as
    Note objects.
    
    Attributes:
        bpm (int): Tempo in beats per minute
        program (int): MIDI program number (instrument), 0-127
        midi_file (MidiFile): The underlying mido MidiFile object
        track (MidiTrack): The current track being written to
    
    MIDI Program Numbers (General MIDI):
        0-7: Piano
        8-15: Chromatic Percussion
        16-23: Organ
        24-31: Guitar
        32-39: Bass
        40-47: Strings
        48-55: Ensemble
        56-63: Brass
        64-71: Reed
        72-79: Pipe
        80-87: Synth Lead
        88-95: Synth Pad
        96-103: Synth Effects
        104-111: Ethnic
        112-119: Percussive
        120-127: Sound Effects
    
    Example:
        >>> writer = MidiWriter(bpm=120, program=0)
        >>> writer.add_note('C4', velocity=80, duration_beats=1.0)
        >>> writer.add_note('E4', velocity=80, duration_beats=1.0)
        >>> writer.add_note('G4', velocity=80, duration_beats=1.0)
        >>> writer.save('melody.mid')
    """
    
    def __init__(self, bpm: int = 120, program: int = 0):
        """
        Initialize the MidiWriter with tempo and instrument.
        
        Args:
            bpm: Tempo in beats per minute. Default is 120 (moderate tempo).
            program: MIDI program number (0-127) for instrument selection.
                    Default is 0 (Acoustic Grand Piano in General MIDI).
        
        Raises:
            ValueError: If program is outside valid range 0-127.
        """
        if not 0 <= program <= 127:
            raise ValueError(f"Program must be 0-127, got {program}")
        
        self.bpm = bpm
        self.program = program
        
        # Create MIDI file and track
        self.midi_file = MidiFile()
        self.track = MidiTrack()
        self.midi_file.tracks.append(self.track)
        
        # Add program change message to set the instrument
        self.track.append(Message('program_change', program=program, time=0))
    
    def note_name_to_number(self, note_name: str) -> int:
        """
        Convert a note name (e.g., 'C4', 'F#5') to MIDI note number.
        
        The note name format is: <pitch><octave>
        - Pitch: C, C#, Db, D, D#, Eb, E, F, F#, Gb, G, G#, Ab, A, A#, Bb, B
        - Octave: Integer (typically -1 to 9)
        
        Args:
            note_name: Note name string like 'C4', 'F#5', 'Bb3'
        
        Returns:
            MIDI note number (0-127)
        
        Raises:
            ValueError: If note name format is invalid.
        
        Example:
            >>> writer = MidiWriter()
            >>> writer.note_name_to_number('C4')
            60
            >>> writer.note_name_to_number('A4')
            69
        """
        if not note_name:
            raise ValueError("Note name cannot be empty")
        
        # Parse the note name - handle sharps and flats
        # Check if second character is # or b (accidental)
        if len(note_name) >= 3 and note_name[1] in '#b':
            note = note_name[:2].lower()
            octave_str = note_name[2:]
        else:
            note = note_name[0].lower()
            octave_str = note_name[1:]
        
        try:
            octave = int(octave_str)
        except ValueError:
            raise ValueError(f"Invalid octave in note name: '{note_name}'")
        
        if note not in NOTE_NAMES:
            raise ValueError(f"Invalid note name: '{note}'")
        
        # Calculate MIDI number: (octave + 1) * 12 + semitone
        return (octave + 1) * 12 + NOTE_NAMES[note]
    
    def beats_to_ticks(self, beats: float) -> int:
        """
        Convert beats to MIDI ticks.
        
        MIDI timing uses ticks, which are subdivisions of a beat.
        Standard resolution is 480 ticks per quarter note (beat).
        
        Args:
            beats: Duration in beats (quarter notes)
        
        Returns:
            Duration in MIDI ticks
        
        Example:
            >>> writer = MidiWriter()
            >>> writer.beats_to_ticks(1.0)  # One beat
            480
            >>> writer.beats_to_ticks(0.5)  # Half beat (eighth note)
            240
        """
        return int(beats * TICKS_PER_BEAT)
    
    def add_note(
        self,
        note: Union[str, Note, int],
        velocity: int = 64,
        duration_beats: float = 1.0,
        start_beats: float = 0
    ) -> None:
        """
        Add a single note to the MIDI file.
        
        Args:
            note: Note to add. Can be:
                - String like 'C4', 'F#5'
                - Note object
                - MIDI note number (int)
            velocity: Volume/intensity of the note (0-127). Default is 64.
            duration_beats: How long the note plays in beats. Default is 1.0.
            start_beats: Offset from current position in beats. Default is 0.
        
        Raises:
            ValueError: If note format is invalid or velocity out of range.
        
        Example:
            >>> writer = MidiWriter()
            >>> writer.add_note('C4', velocity=80, duration_beats=1.0)
            >>> writer.add_note('E4', velocity=80, duration_beats=0.5)
        """
        # Convert note to MIDI number
        if isinstance(note, str):
            note_number = self.note_name_to_number(note)
        elif isinstance(note, Note):
            note_number = note.midi_number
        elif isinstance(note, int):
            note_number = note
        else:
            raise ValueError(f"Invalid note type: {type(note)}")
        
        # Validate velocity
        velocity = max(0, min(127, velocity))
        
        # Convert beats to ticks
        time_ticks = self.beats_to_ticks(start_beats)
        duration_ticks = self.beats_to_ticks(duration_beats)
        
        # Add note_on message (note starts)
        self.track.append(Message(
            'note_on',
            note=note_number,
            velocity=velocity,
            time=time_ticks
        ))
        
        # Add note_off message (note ends)
        self.track.append(Message(
            'note_off',
            note=note_number,
            velocity=velocity,
            time=duration_ticks
        ))
    
    def add_chord(
        self,
        notes: List[Union[str, Note, int]],
        velocity: int = 64,
        duration_beats: float = 1.0,
        start_beats: float = 0
    ) -> None:
        """
        Add a chord (multiple simultaneous notes) to the MIDI file.
        
        All notes in the chord start and end at the same time.
        
        Args:
            notes: List of notes to play together. Each can be:
                - String like 'C4', 'F#5'
                - Note object
                - MIDI note number (int)
            velocity: Volume/intensity of all notes (0-127). Default is 64.
            duration_beats: How long the chord plays in beats. Default is 1.0.
            start_beats: Offset from current position in beats. Default is 0.
        
        Example:
            >>> writer = MidiWriter()
            >>> writer.add_chord(['C4', 'E4', 'G4'], velocity=80, duration_beats=2.0)
        """
        if not notes:
            return
        
        # Convert all notes to MIDI numbers
        note_numbers = []
        for note in notes:
            if isinstance(note, str):
                note_numbers.append(self.note_name_to_number(note))
            elif isinstance(note, Note):
                note_numbers.append(note.midi_number)
            elif isinstance(note, int):
                note_numbers.append(note)
            else:
                raise ValueError(f"Invalid note type: {type(note)}")
        
        # Validate velocity
        velocity = max(0, min(127, velocity))
        
        # Convert beats to ticks
        time_ticks = self.beats_to_ticks(start_beats)
        duration_ticks = self.beats_to_ticks(duration_beats)
        
        # Add all note_on messages (only first has time offset)
        for i, note_number in enumerate(note_numbers):
            self.track.append(Message(
                'note_on',
                note=note_number,
                velocity=velocity,
                time=time_ticks if i == 0 else 0
            ))
        
        # Add all note_off messages (only first has duration)
        for i, note_number in enumerate(note_numbers):
            self.track.append(Message(
                'note_off',
                note=note_number,
                velocity=velocity,
                time=duration_ticks if i == 0 else 0
            ))
    
    def add_rest(self, duration_beats: float) -> None:
        """
        Add a rest (silence) to the MIDI file.
        
        This is implemented by adding a silent note (velocity 0).
        
        Args:
            duration_beats: Duration of rest in beats.
        
        Example:
            >>> writer = MidiWriter()
            >>> writer.add_note('C4', duration_beats=1.0)
            >>> writer.add_rest(duration_beats=0.5)  # Half-beat rest
            >>> writer.add_note('E4', duration_beats=1.0)
        """
        # Add a silent note to create the rest duration
        duration_ticks = self.beats_to_ticks(duration_beats)
        self.track.append(Message(
            'note_on',
            note=60,  # Middle C (doesn't matter, velocity is 0)
            velocity=0,
            time=0
        ))
        self.track.append(Message(
            'note_off',
            note=60,
            velocity=0,
            time=duration_ticks
        ))
    
    def save(self, filename: str) -> None:
        """
        Save the MIDI file to disk.
        
        Args:
            filename: Path/filename to save the MIDI file.
                     Should have .mid or .midi extension.
        
        Example:
            >>> writer = MidiWriter()
            >>> writer.add_note('C4', duration_beats=1.0)
            >>> writer.save('output.mid')
        """
        self.midi_file.save(filename)
    
    def reset(self) -> None:
        """
        Clear the current track and start fresh.
        
        Useful for generating multiple MIDI files with the same writer.
        Preserves BPM and program settings.
        """
        self.midi_file = MidiFile()
        self.track = MidiTrack()
        self.midi_file.tracks.append(self.track)
        self.track.append(Message('program_change', program=self.program, time=0))
    
    def __repr__(self) -> str:
        return f"MidiWriter(bpm={self.bpm}, program={self.program})"