# arpeggiator.py
from midi_generator import MidiGenerator
from group_gen import generate_permutation_sequences

class Arpeggiator:
    # Major scale degrees (1-indexed)
    MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]
    
    # Chord types (triads and seventh chords)
    CHORD_TYPES = {
        'major': [0, 4, 7],
        'minor': [0, 3, 7],
        'diminished': [0, 3, 6],
        'augmented': [0, 4, 8],
        'major7': [0, 4, 7, 11],
        'minor7': [0, 3, 7, 10],
        'dominant7': [0, 4, 7, 10],
        'diminished7': [0, 3, 6, 9],
        'half_diminished7': [0, 3, 6, 10]
    }
    
    # Common chord progressions for each scale degree in major keys
    SCALE_DEGREE_CHORD_TYPES = {
        1: 'major',  # I chord
        2: 'minor',  # ii chord
        3: 'minor',  # iii chord
        4: 'major',  # IV chord
        5: 'major',  # V chord (could also be dominant7)
        6: 'minor',  # vi chord
        7: 'diminished'  # viio chord
    }
    
    # Common arpeggio patterns (0-indexed within chord)
    ARPEGGIO_PATTERNS = {
        'up': lambda notes, count: [notes[i % len(notes)] for i in range(count)],
        'down': lambda notes, count: [notes[len(notes) - 1 - (i % len(notes))] for i in range(count)],
        'up_down': lambda notes, count: [notes[i % (2 * len(notes) - 2)] if i % (2 * len(notes) - 2) < len(notes) 
                                      else notes[2 * len(notes) - 2 - (i % (2 * len(notes) - 2))] for i in range(count)],
        'group': generate_permutation_sequences
    }
    
    def __init__(self, key='c', octave=4, bpm=120, program=0):
        """Initialize the Arpeggiator with key, octave, BPM, and MIDI program.
        
        Args:
            key (str): The musical key (default 'c')
            octave (int): Starting octave (default 4)
            bpm (int): Beats per minute (default 120)
            program (int): MIDI program number (default 0)
        """
        self.midi_gen = MidiGenerator(bpm=bpm, program=program)
        self.key = key.lower()
        self.octave = octave
        self.current_beat = 0
        
        # Calculate the root note of the key
        if self.key not in self.midi_gen.NOTE_NAMES:
            raise ValueError(f"Invalid key: {key}")
        self.key_root = self.midi_gen.NOTE_NAMES[self.key]
    
    def degree_to_notes(self, degree, chord_type=None, octave=None):
        """Convert a scale degree to a list of note names for the corresponding chord.
        
        Args:
            degree (int): Scale degree (1-7)
            chord_type (str, optional): Type of chord to generate
            octave (int, optional): Octave for the chord
            
        Returns:
            list: List of note names with octave (e.g., ['C4', 'E4', 'G4'])
        """
        if octave is None:
            octave = self.octave
            
        # Normalize degree to 1-7
        degree = ((degree - 1) % 7) + 1
        
        # Get the chord type based on scale degree if not specified
        if chord_type is None:
            chord_type = self.SCALE_DEGREE_CHORD_TYPES[degree]
        
        # Calculate the root note of the chord
        scale_position = degree - 1  # Convert to 0-indexed
        root_note_value = (self.key_root + self.MAJOR_SCALE[scale_position]) % 12
        
        # Find the note name for this value
        root_note_name = None
        for name, value in self.midi_gen.NOTE_NAMES.items():
            if value == root_note_value:
                # Prefer natural or sharp notes over flats for simplicity
                if len(name) == 1 or name.endswith('#'):
                    root_note_name = name
                    break
        
        if root_note_name is None:
            for name, value in self.midi_gen.NOTE_NAMES.items():
                if value == root_note_value:
                    root_note_name = name
                    break
                    
        # Get the chord intervals
        intervals = self.CHORD_TYPES[chord_type]
        
        # Generate note names
        note_names = []
        for interval in intervals:
            # Calculate actual note value
            note_value = (root_note_value + interval) % 12
            
            # Find the octave adjustment
            octave_adjust = (root_note_value + interval) // 12
            current_octave = octave + octave_adjust
            
            # Find the note name
            for name, value in self.midi_gen.NOTE_NAMES.items():
                if value == note_value:
                    # Prefer natural or sharp notes
                    if len(name) == 1 or name.endswith('#'):
                        note_names.append(f"{name}{current_octave}")
                        break
            
            # If no note name was added, use any available name
            if len(note_names) != len(intervals[:intervals.index(interval) + 1]):
                for name, value in self.midi_gen.NOTE_NAMES.items():
                    if value == note_value:
                        note_names.append(f"{name}{current_octave}")
                        break
        
        return note_names
    
    def generate_arpeggio(self, progression, durations, notes_per_chord=8, 
                         pattern='up', note_duration=0.25, velocity=64, spacing_factor=1.0):
        """Generate an arpeggio sequence based on a chord progression with adjustable note spacing.
        
        Args:
            progression (list): List of integers representing scale degrees (1-7)
            durations (list): List of durations for each chord in beats
            notes_per_chord (int): Number of arpeggio notes to play per chord (default 8)
            pattern (str): Arpeggio pattern to use ('up', 'down', or 'up_down') (default 'up')
            note_duration (float): Duration of each note in beats (default 0.25)
            velocity (int): MIDI velocity (0-127) (default 64)
            spacing_factor (float): Factor to adjust spacing between notes (default 1.0)
            
        Returns:
            None
        """
        if len(progression) != len(durations):
            raise ValueError("Progression and durations must have the same length")
        
        if pattern not in self.ARPEGGIO_PATTERNS:
            raise ValueError(f"Unknown pattern: {pattern}. Available patterns: {list(self.ARPEGGIO_PATTERNS.keys())}")
        
        for chord_degree, chord_duration in zip(progression, durations):
            # Get the notes for this chord
            chord_notes = self.degree_to_notes(chord_degree)
            
            # Generate the arpeggio pattern
            pattern_func = self.ARPEGGIO_PATTERNS[pattern]
            if pattern_func == generate_permutation_sequences:
                self.group_pattern_to_notes()
            else:
                arpeggio_notes = pattern_func(chord_notes, notes_per_chord)
            
            # Calculate the base time between notes and apply spacing factor
            base_time_between_notes = (chord_duration / notes_per_chord) * spacing_factor
            
            # Add the notes to the MIDI file with adjusted spacing
            # TODO: I guess this is where the stream would go or sm like that
            for i, note in enumerate(arpeggio_notes):
                start_beat = self.current_beat
                self.midi_gen.add_note(note, velocity=velocity, 
                                     duration_beats=note_duration)
            
            # Update the current beat position to account for total duration including spacing
            self.current_beat += chord_duration * spacing_factor

    def group_pattern_to_notes(self):
        """map the generated patter to current notes"""
        pass
    
    def save(self, filename):
        """Save the generated MIDI file.
        
        Args:
            filename (str): Name of the file to save
            
        Returns:
            None
        """
        self.midi_gen.save(filename)


# Example usage
if __name__ == "__main__":
    # Create an arpeggiator in C major at 120 BPM
    arp = Arpeggiator(key='c', octave=4, bpm=120, program=0)
    
    # Generate a 2-5-1 progression in C major
    # 2-5-1 corresponds to Dm-G-C chords in C major
    progression = [2, 5, 1]  # ii-V-I
    durations = [1, 1, 1]     # 2 beats, 2 beats, 4 beats
    
    # Generate an arpeggio with 8 notes per chord, in an up pattern, with default spacing
    arp.generate_arpeggio(progression=progression, durations=durations,
                        notes_per_chord=8, pattern='up', note_duration=1, spacing_factor=1.0)
    
    # Add another progression
    progression = [6, 4, 5, 1]  # vi-IV-V-I (Am-F-G-C in C major)
    durations = [1, 1, 1, 1]     # 2 beats each for the first three, 4 for the last
    
    # This time use an up_down pattern with increased spacing
    #arp.generate_arpeggio(progression=progression, durations=durations,
    #                    notes_per_chord=8, pattern='up_down', note_duration=.5, spacing_factor=1.2)
    
    # Save the result
    arp.save('arpeggio_progression.mid') 