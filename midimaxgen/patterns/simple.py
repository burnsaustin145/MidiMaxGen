"""
Simple arpeggio patterns for MidiMaxGen.

This module provides traditional arpeggio patterns like up, down, and up_down.
These are the most common arpeggio patterns used in music.

Pattern Types:
    up: Notes played from lowest to highest, then repeating
        Example: C-E-G-C-E-G-C-E (for C major chord)
    
    down: Notes played from highest to lowest, then repeating
        Example: G-E-C-G-E-C-G-E (for C major chord)
    
    up_down: Notes played up then down (ping-pong/bounce)
        Example: C-E-G-E-C-E-G-E (for C major chord)
        Note: The top and bottom notes are NOT repeated at the turnaround

Example:
    >>> pattern = SimplePattern('up')
    >>> pattern.generate(['C4', 'E4', 'G4'], count=8)
    ['C4', 'E4', 'G4', 'C4', 'E4', 'G4', 'C4', 'E4']
"""

from typing import List, Any, Optional, Callable
from midimaxgen.patterns.base import Pattern


def _up_pattern(notes: List[Any], count: int) -> List[Any]:
    """
    Generate ascending (up) arpeggio pattern.
    
    Notes cycle through from first to last, repeating as needed.
    
    Args:
        notes: List of notes to arpeggiate
        count: Number of notes to generate
    
    Returns:
        List of notes in ascending cyclic order
    """
    if not notes:
        return []
    return [notes[i % len(notes)] for i in range(count)]


def _down_pattern(notes: List[Any], count: int) -> List[Any]:
    """
    Generate descending (down) arpeggio pattern.
    
    Notes cycle through from last to first, repeating as needed.
    
    Args:
        notes: List of notes to arpeggiate
        count: Number of notes to generate
    
    Returns:
        List of notes in descending cyclic order
    """
    if not notes:
        return []
    n = len(notes)
    return [notes[n - 1 - (i % n)] for i in range(count)]


def _up_down_pattern(notes: List[Any], count: int) -> List[Any]:
    """
    Generate ping-pong (up-down) arpeggio pattern.
    
    Notes go up to the top, then back down, without repeating
    the top or bottom notes at the turnaround points.
    
    For a 3-note chord [C, E, G], the cycle is: C-E-G-E-C-E-G-E...
    (4 notes per cycle = 2 * len - 2)
    
    Args:
        notes: List of notes to arpeggiate
        count: Number of notes to generate
    
    Returns:
        List of notes in up-down pattern
    """
    if not notes:
        return []
    if len(notes) == 1:
        return [notes[0]] * count
    
    # Create one full cycle: up then down (without repeating endpoints)
    # For [C, E, G]: cycle = [C, E, G, E] (length = 2*3 - 2 = 4)
    cycle_length = 2 * len(notes) - 2
    
    result = []
    for i in range(count):
        pos = i % cycle_length
        if pos < len(notes):
            # Going up
            result.append(notes[pos])
        else:
            # Going down (mirror position)
            mirror_pos = cycle_length - pos
            result.append(notes[mirror_pos])
    
    return result


# Available simple pattern types and their generator functions
SIMPLE_PATTERN_TYPES = {
    'up': _up_pattern,
    'down': _down_pattern,
    'up_down': _up_down_pattern,
}


class SimplePattern(Pattern):
    """
    Simple arpeggio pattern generator.
    
    Implements traditional arpeggio patterns like ascending (up),
    descending (down), and ping-pong (up_down).
    
    Attributes:
        pattern_type (str): Type of pattern ('up', 'down', 'up_down')
    
    Example:
        >>> up = SimplePattern('up')
        >>> up.generate(['C4', 'E4', 'G4'], count=6)
        ['C4', 'E4', 'G4', 'C4', 'E4', 'G4']
        
        >>> down = SimplePattern('down')
        >>> down.generate(['C4', 'E4', 'G4'], count=6)
        ['G4', 'E4', 'C4', 'G4', 'E4', 'C4']
        
        >>> updown = SimplePattern('up_down')
        >>> updown.generate(['C4', 'E4', 'G4'], count=8)
        ['C4', 'E4', 'G4', 'E4', 'C4', 'E4', 'G4', 'E4']
    """
    
    def __init__(self, pattern_type: str = 'up'):
        """
        Initialize a SimplePattern with the specified type.
        
        Args:
            pattern_type: Type of pattern - 'up', 'down', or 'up_down'.
                         Default is 'up'.
        
        Raises:
            ValueError: If pattern_type is not recognized.
        """
        if pattern_type not in SIMPLE_PATTERN_TYPES:
            raise ValueError(
                f"Unknown pattern type: '{pattern_type}'. "
                f"Available types: {list(SIMPLE_PATTERN_TYPES.keys())}"
            )
        
        super().__init__(f'simple_{pattern_type}')
        self.pattern_type = pattern_type
        self._generator = SIMPLE_PATTERN_TYPES[pattern_type]
    
    def generate(
        self, 
        notes: List[Any], 
        count: Optional[int] = None,
        **kwargs
    ) -> List[Any]:
        """
        Generate a sequence of notes following this pattern.
        
        Args:
            notes: List of notes to arpeggiate (chord tones)
            count: Number of notes to generate. Defaults to 8 if not specified.
            **kwargs: Ignored (for interface compatibility)
        
        Returns:
            List of notes arranged according to the pattern.
        
        Example:
            >>> pattern = SimplePattern('up')
            >>> pattern.generate(['C4', 'E4', 'G4'], count=5)
            ['C4', 'E4', 'G4', 'C4', 'E4']
        """
        if count is None:
            count = 8  # Default to 8 notes
        
        if count <= 0:
            return []
        
        return self._generator(notes, count)
    
    @classmethod
    def available_types(cls) -> List[str]:
        """
        Get list of available pattern types.
        
        Returns:
            List of pattern type names.
        """
        return list(SIMPLE_PATTERN_TYPES.keys())