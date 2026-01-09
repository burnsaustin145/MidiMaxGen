"""
Base Pattern class for MidiMaxGen.

This module defines the abstract interface that all pattern generators must implement.
Patterns determine the order in which notes are played in an arpeggio.

Creating Custom Patterns:
    To create a custom pattern, subclass Pattern and implement the generate() method:
    
    class MyPattern(Pattern):
        def generate(self, notes, count=None, **kwargs):
            # Your custom logic here
            return reordered_notes

Example:
    >>> class ReversePattern(Pattern):
    ...     def generate(self, notes, count=None, **kwargs):
    ...         reversed_notes = list(reversed(notes))
    ...         if count:
    ...             return (reversed_notes * ((count // len(notes)) + 1))[:count]
    ...         return reversed_notes
"""

from abc import ABC, abstractmethod
from typing import List, Any, Optional


class Pattern(ABC):
    """
    Abstract base class for arpeggio pattern generators.
    
    All pattern generators should inherit from this class and implement
    the generate() method. This ensures a consistent interface across
    all pattern types.
    
    Patterns transform a list of notes (typically chord tones) into
    a sequence that defines the arpeggio order.
    
    Attributes:
        name (str): Identifier for this pattern type
    
    Example:
        >>> class UpPattern(Pattern):
        ...     def __init__(self):
        ...         super().__init__('up')
        ...     
        ...     def generate(self, notes, count=8, **kwargs):
        ...         return [notes[i % len(notes)] for i in range(count)]
    """
    
    def __init__(self, name: str):
        """
        Initialize the pattern with a name.
        
        Args:
            name: Identifier for this pattern type (e.g., 'up', 'down', 'group')
        """
        self.name = name
    
    @abstractmethod
    def generate(
        self, 
        notes: List[Any], 
        count: Optional[int] = None,
        **kwargs
    ) -> List[Any]:
        """
        Generate a sequence of notes following this pattern.
        
        This method takes a list of notes (usually chord tones) and returns
        them in a specific order based on the pattern logic.
        
        Args:
            notes: List of notes to arrange. Can be Note objects, strings,
                   or any type that represents a musical note.
            count: Number of notes to generate. If None, the pattern may
                   return all possible permutations or a default length.
            **kwargs: Additional pattern-specific parameters.
        
        Returns:
            List of notes arranged according to the pattern.
        
        Example:
            >>> pattern = UpPattern()
            >>> pattern.generate(['C4', 'E4', 'G4'], count=8)
            ['C4', 'E4', 'G4', 'C4', 'E4', 'G4', 'C4', 'E4']
        """
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.name}')"
    
    def __str__(self) -> str:
        return self.name