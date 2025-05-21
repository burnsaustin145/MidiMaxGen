from mido import MidiFile, MidiTrack, Message

class MidiGenerator:
    NOTE_NAMES = {
        'c': 0, 'c#': 1, 'db': 1, 'd': 2, 'd#': 3, 'eb': 3,
        'e': 4, 'f': 5, 'f#': 6, 'gb': 6, 'g': 7, 'g#': 8,
        'ab': 8, 'a': 9, 'a#': 10, 'bb': 10, 'b': 11
    }

    def __init__(self, bpm=120, program=0):
        self.midi_file = MidiFile()
        self.track = MidiTrack()
        self.midi_file.tracks.append(self.track)
        self.bpm = bpm

        # Add program change message
        self.track.append(Message('program_change', program=program, time=0))

    def note_name_to_number(self, note_name):
        """Convert note name like 'c4', 'd#5' to MIDI note number"""
        if not note_name:
            raise ValueError("Note name cannot be empty")

        # Handle flats and sharps
        note = note_name[:-1].lower()
        octave = int(note_name[-1])

        if note not in self.NOTE_NAMES:
            raise ValueError(f"Invalid note name: {note}")

        return self.NOTE_NAMES[note] + (octave + 1) * 12

    def beats_to_ticks(self, beats):
        """Convert beats to MIDI ticks based on current BPM"""
        # MIDI standard: 480 ticks per quarter note
        ticks_per_beat = 480
        return int(beats * ticks_per_beat)

    def add_note(self, note_name, velocity=64, duration_beats=1.0, start_beats=0):
        """Add a note by name with duration in beats"""
        note_number = self.note_name_to_number(note_name)

        # Convert beats to ticks
        time_ticks = self.beats_to_ticks(start_beats)
        duration_ticks = self.beats_to_ticks(duration_beats)

        # Add note on and note off messages
        self.track.append(Message('note_on', note=note_number, velocity=velocity, time=time_ticks))
        self.track.append(Message('note_off', note=note_number, velocity=velocity, time=duration_ticks))

    def add_chord(self, note_names, velocity=64, duration_beats=1.0, start_beats=0):
        """Add multiple notes at once to form a chord"""
        if not note_names:
            return

        # Convert all notes to MIDI numbers
        note_numbers = [self.note_name_to_number(name) for name in note_names]

        # Convert beats to ticks
        time_ticks = self.beats_to_ticks(start_beats)
        duration_ticks = self.beats_to_ticks(duration_beats)

        # Add note on messages (all at once)
        for i, note_number in enumerate(note_numbers):
            # Only the first note has the time offset
            self.track.append(Message('note_on', note=note_number, velocity=velocity,
                                     time=time_ticks if i == 0 else 0))

        # Add note off messages
        for i, note_number in enumerate(note_numbers):
            # Only the first note off has the duration time
            self.track.append(Message('note_off', note=note_number, velocity=velocity,
                                     time=duration_ticks if i == 0 else 0))

    def save(self, filename):
        """Save the MIDI file"""
        self.midi_file.save(filename)


# Example usage:
if __name__ == "__main__":
    midi = MidiGenerator(bpm=120, program=12)

    # Add individual notes
    midi.add_note('c4', duration_beats=1.0, start_beats=0)
    midi.add_note('e4', duration_beats=1.0, start_beats=1.0)
    midi.add_note('g4', duration_beats=1.0, start_beats=2.0)

    # Add a chord
    midi.add_chord(['c5', 'e5', 'g5'], duration_beats=2.0, start_beats=3.0)

    midi.save('my_midi_file.mid')