"""
MIDI Arpeggiator Visualizer

Generates animated visualizations of permutation-based arpeggio patterns
using Pillow for frame generation and ffmpeg for video encoding.

This is a standalone visualization tool that uses the midimaxgen library
to generate MIDI patterns and visualizes them as animated circles.

Usage:
    python midi_visualizer.py --bpm 120 --permutation-size 4 --key C --output output.mp4
"""

import os
import sys
import argparse
import shutil
import subprocess
from pathlib import Path
from typing import List, Tuple, Optional
from dataclasses import dataclass
from math import factorial

# Add parent directory to path to import midimaxgen
sys.path.insert(0, str(Path(__file__).parent.parent))

from PIL import Image, ImageDraw, ImageFont

from midimaxgen.arpeggiator import Arpeggiator
from midimaxgen.patterns.group import generate_permutation_sequences


# Constants
WIDTH = 1080
HEIGHT = 1920
FPS = 60
BACKGROUND_COLOR = (20, 20, 30)  # Dark blue-gray
CIRCLE_OFF_COLOR = (60, 60, 80)  # Dim gray-blue
CIRCLE_ON_COLORS = [
    (255, 100, 100),  # Red
    (100, 255, 100),  # Green
    (100, 100, 255),  # Blue
    (255, 255, 100),  # Yellow
    (255, 100, 255),  # Magenta
    (100, 255, 255),  # Cyan
    (255, 180, 100),  # Orange
    (180, 100, 255),  # Purple
]


@dataclass
class NoteEvent:
    """Represents a single note event with timing information."""
    note_name: str
    circle_index: int  # Which circle (0 to n-1) this note triggers
    start_frame: int
    end_frame: int
    permutation_index: int  # Which permutation this belongs to
    position_in_permutation: int  # Position within the permutation (0 to n-1)


def calculate_frames_per_beat(bpm: int) -> float:
    """Calculate how many frames per beat at given BPM."""
    beats_per_second = bpm / 60.0
    return FPS / beats_per_second


def generate_note_events(
    arpeggiator: Arpeggiator,
    progression: List[int],
    permutation_size: int,
    order: str,
    note_duration_beats: float,
    bpm: int
) -> Tuple[List[NoteEvent], int]:
    """
    Generate note events with frame timing from arpeggiator patterns.
    
    Returns:
        Tuple of (list of NoteEvents, total frame count)
    """
    # Get permutations
    
    # Get chord notes for each degree in progression
    all_notes = arpeggiator._generate_group_pattern(progression=progression,
                                                    order=order,
                                                    subgroup=None,
                                                    permutation_size=permutation_size)

    frames_per_beat = calculate_frames_per_beat(bpm)
    frames_per_note = int(frames_per_beat * note_duration_beats)
    
    events = []
    current_frame = 0
    print(all_notes)
    for note in all_notes:
        idx = arpeggiator.note_to_chord_position(note, 6, 'minor7') - 1
        event = NoteEvent(
            note_name=note,
            circle_index=idx,
            start_frame=current_frame,
            end_frame=current_frame + frames_per_note,
            permutation_index=idx,
            position_in_permutation=idx
        )
        events.append(event)
        current_frame += frames_per_note
    
    total_frames = current_frame
    return events, total_frames


def get_active_circles(events: List[NoteEvent], frame: int, n: int) -> List[Tuple[int, str]]:
    """
    Get which circles are active at a given frame.
    
    Returns:
        List of (circle_index, note_name) tuples for active circles
    """
    active = []
    for event in events:
        if event.start_frame <= frame < event.end_frame:
            active.append((event.circle_index, event.note_name))
    return active


def draw_frame(
    n: int,
    active_circles: List[Tuple[int, str]],
    frame_num: int,
    total_frames: int,
    current_permutation: Optional[Tuple] = None,
    bpm: int = 120
) -> Image.Image:
    """
    Draw a single frame with n circles.
    
    Args:
        n: Number of circles (permutation size)
        active_circles: List of (circle_index, note_name) for lit circles
        frame_num: Current frame number
        total_frames: Total frame count
        current_permutation: Current permutation tuple for display
        bpm: BPM for display
    
    Returns:
        PIL Image object
    """
    img = Image.new('RGB', (WIDTH, HEIGHT), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Calculate circle layout - VERTICAL stacking, lowest pitch at bottom
    circle_radius = HEIGHT // (n * 2)
    total_height = n * (circle_radius * 2 + 20) - 20
    center_x = WIDTH // 2
    start_y = (HEIGHT - total_height) // 2 + circle_radius
    
    # Create set of active circle indices for quick lookup
    active_indices = {idx for idx, _ in active_circles}
    active_notes = {idx: note for idx, note in active_circles}
    
    # Draw circles - reversed so index 0 (lowest pitch) is at bottom
    for i in range(n):
        x = center_x
        # Reverse: highest index at top, lowest at bottom
        y = start_y + (n - 1 - i) * (circle_radius * 2 + 20)
        
        if i in active_indices:
            # Active circle - lit up
            color = CIRCLE_ON_COLORS[i % len(CIRCLE_ON_COLORS)]
            # Draw glow effect
            for glow_size in range(3, 0, -1):
                glow_radius = circle_radius + glow_size * 10
                glow_color = tuple(max(0, c - 50 * glow_size) for c in color)
                draw.ellipse(
                    [x - glow_radius, y - glow_radius, x + glow_radius, y + glow_radius],
                    fill=glow_color
                )
            draw.ellipse(
                [x - circle_radius, y - circle_radius, x + circle_radius, y + circle_radius],
                fill=color
            )
            # Draw note name
            note = active_notes.get(i, "")
            try:
                font = ImageFont.truetype("arial.ttf", 32)
            except:
                font = ImageFont.load_default()
            bbox = draw.textbbox((0, 0), note, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            draw.text(
                (x - text_width // 2, y - text_height // 2),
                note,
                fill=(0, 0, 0),
                font=font
            )
        else:
            # Inactive circle - dim
            draw.ellipse(
                [x - circle_radius, y - circle_radius, x + circle_radius, y + circle_radius],
                fill=CIRCLE_OFF_COLOR
            )
        
        # Draw circle number to the right
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        label = str(i + 1)  # 1-based for display
        bbox = draw.textbbox((0, 0), label, font=font)
        text_height = bbox[3] - bbox[1]
        draw.text(
            (x + circle_radius + 20, y - text_height // 2),
            label,
            fill=(150, 150, 170),
            font=font
        )
    
    # Draw info text at top
    try:
        font_large = ImageFont.truetype("arial.ttf", 36)
        font_small = ImageFont.truetype("arial.ttf", 24)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Title
    title = f"Permutation Arpeggiator (n={n}, {factorial(n)} permutations)"
    draw.text((20, 20), title, fill=(200, 200, 220), font=font_large)
    
    # Current permutation
    if current_permutation:
        perm_text = f"Current: {current_permutation}"
        draw.text((20, 70), perm_text, fill=(150, 150, 170), font=font_small)
    
    # BPM and frame info
    info_text = f"BPM: {bpm} | Frame: {frame_num}/{total_frames}"
    draw.text((20, HEIGHT - 50), info_text, fill=(150, 150, 170), font=font_small)
    
    # Progress bar at bottom
    progress = frame_num / total_frames if total_frames > 0 else 0
    bar_height = 10
    bar_y = HEIGHT - bar_height - 10
    draw.rectangle([0, bar_y, WIDTH, bar_y + bar_height], fill=(40, 40, 50))
    draw.rectangle([0, bar_y, int(WIDTH * progress), bar_y + bar_height], fill=(100, 200, 255))
    
    return img


def get_current_permutation(events: List[NoteEvent], frame: int, perms: List[Tuple]) -> Optional[Tuple]:
    """Get the current permutation being played at this frame."""
    for event in events:
        if event.start_frame <= frame < event.end_frame:
            if event.permutation_index < len(perms):
                return perms[event.permutation_index]
    return None


def generate_frames(
    output_dir: Path,
    n: int,
    bpm: int,
    key: str,
    progression: List[int],
    order: str,
    note_duration_beats: float
) -> int:
    """
    Generate all frames as PNG files.
    
    Returns:
        Total number of frames generated
    """
    # Create arpeggiator
    arp = Arpeggiator(key=key, octave=4, bpm=bpm)
    
    # Generate note events
    events, total_frames = generate_note_events(
        arpeggiator=arp,
        progression=progression,
        permutation_size=n,
        order=order,
        note_duration_beats=note_duration_beats,
        bpm=bpm
    )
    
    # Get permutations for display
    perms = generate_permutation_sequences(n=n, order=order)
    
    print(f"Generating {total_frames} frames for {len(perms)} permutations...")
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate each frame
    for frame in range(total_frames):
        if frame % 60 == 0:
            print(f"  Frame {frame}/{total_frames} ({100*frame/total_frames:.1f}%)")
        
        active = get_active_circles(events, frame, n)
        current_perm = get_current_permutation(events, frame, perms)
        
        img = draw_frame(
            n=n,
            active_circles=active,
            frame_num=frame,
            total_frames=total_frames,
            current_permutation=current_perm,
            bpm=bpm
        )
        
        # Save frame
        img.save(output_dir / f"frame_{frame:06d}.png")
    
    print(f"Generated {total_frames} frames in {output_dir}")
    return total_frames


def stitch_frames_to_video(frames_dir: Path, output_path: Path, fps: int = FPS):
    """
    Use ffmpeg to stitch PNG frames into MP4 video.
    """
    print(f"Stitching frames to video: {output_path}")
    
    # Check if ffmpeg is available
    if shutil.which("ffmpeg") is None:
        print("ERROR: ffmpeg not found in PATH. Please install ffmpeg.")
        print("You can manually stitch frames using:")
        print(f"  ffmpeg -framerate {fps} -i {frames_dir}/frame_%06d.png -c:v libx264 -pix_fmt yuv420p {output_path}")
        return False
    
    cmd = [
        "ffmpeg",
        "-y",  # Overwrite output
        "-framerate", str(fps),
        "-i", str(frames_dir / "frame_%06d.png"),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "18",  # High quality
        str(output_path)
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"Video saved to: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running ffmpeg: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Generate animated visualization of permutation arpeggio patterns"
    )
    parser.add_argument(
        "--bpm", type=int, default=120,
        help="Beats per minute (default: 120)"
    )
    parser.add_argument(
        "--permutation-size", "-n", type=int, default=4,
        help="Size of permutation group S_n (default: 4)"
    )
    parser.add_argument(
        "--key", type=str, default="C",
        help="Musical key (default: C)"
    )
    parser.add_argument(
        "--progression", type=str, default=(6,),
        help="Chord progression as comma-separated scale degrees (default: 6, 5, 4, 6)"
    )
    parser.add_argument(
        "--order", type=str, default="conjugacy",
        choices=["lex", "random", "conjugacy", "coset"],
        help="Permutation ordering (default: conjugacy)"
    )
    parser.add_argument(
        "--note-duration", type=float, default=1,
        help="Duration of each note in beats (default: 0.25 = sixteenth note)"
    )
    parser.add_argument(
        "--output", "-o", type=str, default="output_viz_ex_001_slow.mp4",
        help="Output video file path (default: output.mp4)"
    )
    parser.add_argument(
        "--frames-dir", type=str, default=None,
        help="Directory for intermediate frames (default: temp_frames/)"
    )
    parser.add_argument(
        "--keep-frames", action="store_true",
        help="Keep intermediate frame files after video creation"
    )
    parser.add_argument(
        "--frames-only", action="store_true",
        help="Only generate frames, don't create video"
    )
    
    args = parser.parse_args()
    
    # Parse progression
    progression = args.progression
    
    # Set up paths
    output_path = Path(args.output)
    frames_dir = Path(args.frames_dir) if args.frames_dir else Path("temp_frames")
    
    print("=" * 60)
    print("MIDI Arpeggiator Visualizer")
    print("=" * 60)
    print(f"  Permutation size (n): {args.permutation_size}")
    print(f"  Total permutations: {factorial(args.permutation_size)}")
    print(f"  BPM: {args.bpm}")
    print(f"  Key: {args.key}")
    print(f"  Progression: {progression}")
    print(f"  Order: {args.order}")
    print(f"  Note duration: {args.note_duration} beats")
    print(f"  FPS: {FPS}")
    print("=" * 60)
    
    # Generate frames
    total_frames = generate_frames(
        output_dir=frames_dir,
        n=args.permutation_size,
        bpm=args.bpm,
        key=args.key,
        progression=progression,
        order=args.order,
        note_duration_beats=args.note_duration
    )
    
    if not args.frames_only:
        # Stitch to video
        success = stitch_frames_to_video(frames_dir, output_path)
        
        # Clean up frames if requested
        if success and not args.keep_frames:
            print(f"Cleaning up frames in {frames_dir}")
            shutil.rmtree(frames_dir)
    
    print("Done!")


if __name__ == "__main__":
    main()
