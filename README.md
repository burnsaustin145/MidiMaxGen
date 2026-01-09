# MidiMaxGen

A Python library for generating MIDI arpeggios using traditional patterns and mathematical group theory.

## Overview

MidiMaxGen allows you to create MIDI arpeggios and sequences by combining:
- **Musical theory**: Scales, chords, and diatonic harmony
- **Pattern generation**: Traditional (up, down, ping-pong) and advanced (group theory permutations)
- **MIDI output**: Standard MIDI file creation

## Installation

### Requirements

```bash
pip install -r requirements.txt
```

### Install MidiMaxGen

```bash
# Clone the repository
git clone https://github.com/burnsaustin145/MidiMaxGen.git
cd MidiMaxGen

# Install in development mode (optional)
pip install -e .
```

## Quick Start

### Basic Arpeggio

```python
from midimaxgen import Arpeggiator

# Create an arpeggiator in C major at 120 BPM
arp = Arpeggiator(key='C', octave=4, bpm=120)

# Generate a I-V-vi-IV progression (the most popular chord progression!)
arp.generate_arpeggio(
    progression=[1, 5, 6, 4],  # Scale degrees
    durations=[1, 1, 1, 1],    # Duration of each chord in beats
    pattern='up',              # Ascending arpeggio
    notes_per_chord=8          # 8 notes per chord
)

# Save to MIDI file
arp.save('pop_progression.mid')
```

### Understanding Scale Degrees

Scale degrees represent chords built on each note of the scale:

| Degree | Roman Numeral | Chord Type | In C Major |
|--------|---------------|------------|------------|
| 1 | I | Major | C major |
| 2 | ii | Minor | D minor |
| 3 | iii | Minor | E minor |
| 4 | IV | Major | F major |
| 5 | V | Major | G major |
| 6 | vi | Minor | A minor |
| 7 | vii° | Diminished | B diminished |

### Pattern Types

#### Simple Patterns

```python
# Ascending: C-E-G-C-E-G-C-E...
arp.generate_arpeggio([1], [1], pattern='up', notes_per_chord=8)

# Descending: G-E-C-G-E-C-G-E...
arp.generate_arpeggio([1], [1], pattern='down', notes_per_chord=8)

# Ping-pong: C-E-G-E-C-E-G-E...
arp.generate_arpeggio([1], [1], pattern='up_down', notes_per_chord=8)
```

#### Group Theory Patterns

Group theory patterns use mathematical permutations to create unique, non-repeating note orderings:

```python
# Lexicographic ordering - systematic exploration of all permutations
arp.generate_arpeggio(
    progression=[1, 4, 5, 1],
    durations=[1, 1, 1, 1],
    pattern='group',
    order='lex'
)

# Conjugacy class ordering - grouped by mathematical structure
arp.generate_arpeggio(
    progression=[6, 4, 1, 5],
    durations=[2, 2, 2, 2],
    pattern='group',
    order='conjugacy'
)

# Random ordering - shuffled permutations
arp.generate_arpeggio(
    progression=[1, 5, 6, 4],
    durations=[1, 1, 1, 1],
    pattern='group',
    order='random'
)
```

## Examples

### Example 1: Classic Pop Progression

```python
from midimaxgen import Arpeggiator

arp = Arpeggiator(key='G', octave=4, bpm=100, program=0)  # Piano

# I-V-vi-IV in G major
arp.generate_arpeggio(
    progression=[1, 5, 6, 4],
    durations=[2, 2, 2, 2],
    pattern='up',
    notes_per_chord=16,
    note_duration=0.25,
    velocity=70
)
arp.save('pop_arpeggio.mid')
```

### Example 2: Sad Minor Progression

```python
arp = Arpeggiator(key='A', octave=3, bpm=80, program=4)  # Electric Piano

# vi-IV-I-V starting from the relative minor feel
arp.generate_arpeggio(
    progression=[6, 4, 1, 5],
    durations=[2, 2, 2, 2],
    pattern='up_down',
    notes_per_chord=12,
    velocity=50
)
arp.save('melancholy.mid')
```

### Example 3: Mathematical Exploration

```python
arp = Arpeggiator(key='C', octave=4, bpm=120)

# Use conjugacy class ordering for structured mathematical patterns
arp.generate_arpeggio(
    progression=[1, 4, 5, 1],
    durations=[1, 1, 1, 1],
    pattern='group',
    order='conjugacy',
    permutation_size=4  # S_4 has 24 permutations
)
arp.save('math_arpeggio.mid')
```

### Example 4: Direct Note Control

```python
from midimaxgen import Arpeggiator
from midimaxgen.core import Note, Chord

arp = Arpeggiator(key='C', bpm=120)

# Add individual notes
arp.add_note('C4', velocity=80, duration_beats=0.5)
arp.add_note('E4', velocity=80, duration_beats=0.5)
arp.add_note('G4', velocity=80, duration_beats=0.5)

# Add a chord
arp.add_chord(['C4', 'E4', 'G4'], velocity=100, duration_beats=2.0)

arp.save('custom_notes.mid')
```

## API Reference

### Arpeggiator

The main class for generating arpeggios.

```python
Arpeggiator(key='C', octave=4, bpm=120, program=0)
```

**Parameters:**
- `key`: Musical key (C, D, E, F, G, A, B, with # or b for sharps/flats)
- `octave`: Base octave (0-9, default 4)
- `bpm`: Tempo in beats per minute
- `program`: MIDI program number (0-127, see General MIDI)

**Methods:**
- `generate_arpeggio()`: Generate arpeggio from chord progression
- `add_note()`: Add a single note
- `add_chord()`: Add a chord (simultaneous notes)
- `save()`: Save to MIDI file
- `reset()`: Clear and start fresh

### Core Classes

```python
from midimaxgen.core import Note, Chord, Scale

# Note - represents a single musical note
note = Note('C', 4)  # Middle C
print(note.midi_number)  # 60

# Chord - represents a chord
chord = Chord('C', 'major', octave=4)
print(chord.note_names)  # ['C4', 'E4', 'G4']

# Scale - represents a musical scale
scale = Scale('C', 'major', octave=4)
print(scale.degree_to_chord(5).note_names)  # G major: ['G4', 'B4', 'D5']
```

### Pattern Classes

```python
from midimaxgen.patterns import SimplePattern, GroupPattern

# Simple patterns
up = SimplePattern('up')
notes = up.generate(['C4', 'E4', 'G4'], count=8)

# Group theory patterns
group = GroupPattern(n=3, order='conjugacy')
notes = group.generate(['C4', 'E4', 'G4'])
```

## MIDI Program Numbers

Common General MIDI instruments:

| Program | Instrument |
|---------|------------|
| 0 | Acoustic Grand Piano |
| 4 | Electric Piano |
| 24 | Acoustic Guitar (nylon) |
| 25 | Acoustic Guitar (steel) |
| 33 | Electric Bass (finger) |
| 40 | Violin |
| 48 | String Ensemble |
| 73 | Flute |
| 80 | Synth Lead (square) |

## Project Structure

```
midimaxgen/
├── __init__.py          # Package exports
├── arpeggiator.py       # Main Arpeggiator class
├── core/                # Music theory components
│   ├── note.py          # Note representation
│   ├── chord.py         # Chord representation
│   └── scale.py         # Scale/key representation
├── patterns/            # Pattern generators
│   ├── base.py          # Abstract Pattern interface
│   ├── simple.py        # Simple patterns (up, down, up_down)
│   └── group.py         # Group theory patterns
└── midi/                # MIDI output
    └── writer.py        # MIDI file writer
```

## Mathematical Background

### Symmetric Groups

The group theory patterns use symmetric groups (S_n) - the set of all permutations of n elements.

For a chord with 3 notes (triad), S_3 contains 6 permutations:
- (1,2,3) → C-E-G
- (1,3,2) → C-G-E
- (2,1,3) → E-C-G
- (2,3,1) → E-G-C
- (3,1,2) → G-C-E
- (3,2,1) → G-E-C

### Ordering Types

- **Lexicographic (lex)**: Standard dictionary order
- **Conjugacy**: Grouped by cycle structure (mathematical similarity)
- **Coset**: Organized by subgroup structure
- **Random**: Shuffled for unpredictable patterns

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source. See the repository for license details.