"""
MidiMaxGen - A MIDI generation library using mathematical permutation patterns.

This library allows you to create MIDI arpeggios and sequences using patterns
derived from group theory (symmetric groups) and traditional arpeggio patterns.

Basic Usage:
    from midimaxgen import Arpeggiator
    
    arp = Arpeggiator(key='c', octave=4, bpm=120)
    arp.generate_arpeggio(
        progression=[1, 4, 5, 1],  # I-IV-V-I chord progression
        durations=[1, 1, 1, 1],
        pattern='up'
    )
    arp.save('my_arpeggio.mid')
"""

from midimaxgen.arpeggiator import Arpeggiator
from midimaxgen.midi.writer import MidiWriter
from midimaxgen.patterns import SimplePattern, GroupPattern

__version__ = "1.0.0"
__all__ = ["Arpeggiator", "MidiWriter", "SimplePattern", "GroupPattern"]