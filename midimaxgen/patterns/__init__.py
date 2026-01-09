"""
Pattern generators for MidiMaxGen.

This module provides various arpeggio pattern generators that determine
the order in which chord notes are played.

Pattern Types:
    Simple Patterns:
        - up: Notes played low to high, repeating
        - down: Notes played high to low, repeating
        - up_down: Notes played low-high-low (ping-pong)
    
    Group Theory Patterns:
        - lex: Lexicographic permutation ordering
        - random: Random permutation ordering
        - conjugacy: Grouped by conjugacy classes
        - coset: Ordered by cosets of a subgroup

Example:
    >>> from midimaxgen.patterns import SimplePattern
    >>> pattern = SimplePattern('up')
    >>> pattern.generate(['C4', 'E4', 'G4'], count=8)
    ['C4', 'E4', 'G4', 'C4', 'E4', 'G4', 'C4', 'E4']
"""

from midimaxgen.patterns.base import Pattern
from midimaxgen.patterns.simple import SimplePattern, SIMPLE_PATTERN_TYPES
from midimaxgen.patterns.group import GroupPattern, PERMUTATION_ORDERINGS

__all__ = [
    "Pattern",
    "SimplePattern",
    "SIMPLE_PATTERN_TYPES",
    "GroupPattern",
    "PERMUTATION_ORDERINGS",
]