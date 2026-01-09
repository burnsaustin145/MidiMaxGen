# MIDI Arpeggiator Visualizer

A standalone visualization tool that generates animated videos of permutation-based arpeggio patterns from the MidiMaxGen library.

## Features

- Generates 1920x1080 (16:9) frames at 60 FPS
- Visualizes n circles representing permutation positions
- Circles light up when triggered by MIDI notes
- Displays current permutation, note names, and progress
- Syncs frame timing precisely with BPM
- Stitches frames into MP4 video using ffmpeg

## Requirements

```bash
pip install pillow
pip install sympy  # Required for conjugacy/coset orderings
```

You also need `ffmpeg` installed and available in your PATH for video encoding.

## Usage

Basic usage:
```bash
cd visualizer
python midi_visualizer.py --bpm 120 --permutation-size 3 --key C --output output.mp4
```

Full options:
```bash
python midi_visualizer.py \
    --bpm 120 \
    --permutation-size 4 \
    --key C \
    --progression "1,5,6,4" \
    --order conjugacy \
    --note-duration 0.25 \
    --output my_video.mp4
```

### Command Line Arguments

| Argument | Short | Default | Description |
|----------|-------|---------|-------------|
| `--bpm` | | 120 | Beats per minute |
| `--permutation-size` | `-n` | 3 | Size of permutation group S_n (number of circles) |
| `--key` | | C | Musical key (C, D, E, F, G, A, B with optional # or b) |
| `--progression` | | "1,5,6,4" | Chord progression as scale degrees |
| `--order` | | conjugacy | Permutation ordering: lex, random, conjugacy, coset |
| `--note-duration` | | 0.25 | Duration of each note in beats (0.25 = sixteenth note) |
| `--output` | `-o` | output.mp4 | Output video file path |
| `--frames-dir` | | temp_frames/ | Directory for intermediate frames |
| `--keep-frames` | | false | Keep intermediate frame files |
| `--frames-only` | | false | Only generate frames, don't create video |

## How It Works

1. **Pattern Generation**: Uses MidiMaxGen's arpeggiator with group theory patterns to generate permutation sequences
2. **Timing Calculation**: Converts BPM to frames-per-note to ensure perfect sync at 60 FPS
3. **Frame Rendering**: Uses Pillow to draw each frame with circles, glow effects, and text overlays
4. **Video Encoding**: Uses ffmpeg to stitch PNGs into an MP4

## Timing Math

At 60 FPS with default settings:
- 120 BPM = 2 beats per second
- Each beat = 30 frames
- Each sixteenth note (0.25 beats) = 7.5 frames ≈ 7 frames

For n=3: 6 permutations × 3 notes each = 18 notes
For n=4: 24 permutations × 4 notes each = 96 notes
For n=5: 120 permutations × 5 notes each = 600 notes

## Examples

### Simple triad visualization (n=3)
```bash
python midi_visualizer.py -n 3 --bpm 90 -o triad_demo.mp4
```

### Four-note patterns (n=4)
```bash
python midi_visualizer.py -n 4 --bpm 120 --order lex -o lex_order.mp4
```

### Random ordering with custom progression
```bash
python midi_visualizer.py -n 3 --order random --progression "6,4,1,5" -o random_vi_IV_I_V.mp4
