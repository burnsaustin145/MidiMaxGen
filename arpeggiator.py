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
                         pattern='up', note_duration=0.25, velocity=64, spacing_factor=1.0, order='conjugacy',
                          subgroup=None):
        """Generate an arpeggio sequence based on a chord progression with adjustable note spacing.
        
        Args:
            progression (list): List of integers representing scale degrees (1-7)
            durations (list): List of durations for each chord in beats
            notes_per_chord (int): Number of arpeggio notes to play per chord (default 8)
            pattern (str): Arpeggio pattern to use ('up', 'down', or 'up_down') (default 'up')
            note_duration (float): Duration of each note in beats (default 0.25)
            velocity (int): MIDI velocity (0-127) (default 64)
            spacing_factor (float): Factor to adjust spacing between notes (default 1.0)
            order (string): the permutation ordering to use (default 'conjugacy')
            subgroup (list): subgroup for coset pattern (default 'None')
            
        Returns:
            None
        """
        if len(progression) != len(durations):
            raise ValueError("Progression and durations must have the same length")
        if pattern not in self.ARPEGGIO_PATTERNS:
            raise ValueError(f"Unknown pattern: {pattern}. Available patterns: {list(self.ARPEGGIO_PATTERNS.keys())}")

        arpeggio_notes = []
        chord_duration = 1
        if len(progression) > 1 and pattern == 'group':
            arpeggio_notes = self.group_pattern_to_notes(
                chord_sequence=progression,
                order=order,
                subgroup=None,
                repeat=False
            )
        elif pattern == 'group':
            arpeggio_notes = self.group_pattern_to_notes(
                chord_sequence=progression,
                order=order,
                subgroup=None,
                repeat=True
            )
        else:
            for chord_degree, chord_duration in zip(progression, durations):
                # Get the notes for this chord
                chord_notes = self.degree_to_notes(chord_degree)
                # Generate the arpeggio pattern
                pattern_func = self.ARPEGGIO_PATTERNS[pattern]
                arpeggio_notes = pattern_func(chord_notes, notes_per_chord)


        # TODO: I guess this is where the stream would go or sm like that
        # Add the notes to the MIDI file
        for i, note in enumerate(arpeggio_notes):
            self.midi_gen.add_note(note, velocity=velocity,
                                 duration_beats=note_duration)
            # Update the current beat position to account for total duration including spacing
            self.current_beat += chord_duration * spacing_factor

    def group_pattern_to_notes(self, chord_sequence, order='lex', subgroup=None, repeat=False):
        """
        Generate a sequence of chord notes using permutations from group_gen.py.

        This method applies permutations to reorder the notes of a chord (or chord sequence).
        - For a single chord, permutations will repeat through all possibilities.
        - For a sequence of chords, each permutation can be mapped to the next chord.
        - Permutations are generated for the size of the chord.
        - Returns a list of note names (e.g., ['C4', 'G4', 'E4', ...])

        Args:
            chord_sequence (list of lists): chords for sequence mapping (e.g., [['E4', 'G4', 'B4'], ...]).
            order (str, optional): Permutation ordering ('lex', 'random', 'conjugacy', 'coset'). Defaults to 'lex'.
            subgroup (list, optional): Subgroup for 'coset' ordering (e.g., [(1,2,3), ...]).
            repeat (bool, optional): if true repeat the single chord
        Returns:
            list: A list of permuted note names
        Raises:
            ValueError: If parameters are invalid (e.g., mismatched chord sizes).
        """

        length = len(chord_sequence)
        n = 6 # change n manually for now
        # Generate permutations using group_gen.py

        perms = generate_permutation_sequences(
            n=n,
            length=None,
            order=order,
            subgroup=subgroup
        )
        if len(perms) == 0:
            # Fallback: If no permutations, use the original order repeatedly
            perms = [(i + 1 for i in range(n))] * n
        # Generate the note sequence by applying permutations
        arpeggio_notes = []

        for i, perm in enumerate(perms):
            # Select the current chord (repeat the first or advance in sequence)
            current_chord = self.degree_to_notes(chord_sequence[i % len(chord_sequence)])
            # Convert 1-based permutation to 0-based indices for list access
            indices = [x - 1 for x in perm]
            # Reorder the chord notes based on the permutation
            reordered = [current_chord[idx % 3] for idx in indices if idx < n]  # CHANGE FOR % NUM OF NOTES IN CHORD
            arpeggio_notes.extend(reordered)


        # Trim to exactly notes_per_chord and return
        return arpeggio_notes

    
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
    # === Test Case 4: Group Pattern (using permutation logic) ===
    print("Generating group permutation pattern...")
    arp = Arpeggiator(key='c', octave=4, bpm=120, program=0)
    prog = [6, 4, 3, 6, 6, 4, 3, 2]
    durs = [1, 1, 1, 1, 1, 1, 1, 1]
    new_prog = []
    new_dirs = []
    for i in range(91):
        for p in prog:
            new_prog.append(p)
            new_dirs.append(1)
    arp.generate_arpeggio(
        progression=new_prog,
        durations=new_dirs,
        notes_per_chord=6,
        pattern='group',
        note_duration=0.5,
        spacing_factor=1.0
    )
    arp.save('arpeggio_group.mid')

    print("All patterns generated and saved.")
