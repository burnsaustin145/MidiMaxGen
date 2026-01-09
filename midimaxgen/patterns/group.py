"""
Group theory-based arpeggio patterns for MidiMaxGen.

This module provides advanced arpeggio patterns based on mathematical group theory,
specifically using permutations from symmetric groups. These patterns create unique,
mathematically structured note orderings.

Mathematical Background:
    The symmetric group S_n contains all possible permutations of n elements.
    For a chord with n notes, we can use permutations to generate all possible
    orderings of those notes. Different orderings of permutations create
    different musical effects:
    
    - Lexicographic (lex): Standard dictionary ordering
    - Random: Shuffled permutations for unpredictable patterns
    - Conjugacy: Grouped by cycle structure (mathematical similarity)
    - Coset: Organized by subgroup structure

Permutation Orderings:
    lex: Lexicographic ordering (1,2,3), (1,3,2), (2,1,3), ...
    random: Randomized permutation order
    conjugacy: Grouped by conjugacy classes (similar cycle structures)
    coset: Ordered by cosets of a specified subgroup

Example:
    >>> pattern = GroupPattern(n=3, order='lex')
    >>> pattern.generate(['C4', 'E4', 'G4'])
    ['C4', 'E4', 'G4', 'C4', 'G4', 'E4', 'E4', 'C4', 'G4', ...]

Dependencies:
    This module requires sympy for group theory calculations.
"""

from typing import List, Any, Optional, Tuple
from itertools import permutations
from random import shuffle as random_shuffle

from midimaxgen.patterns.base import Pattern

# Import sympy for group theory operations
try:
    from sympy.combinatorics import Permutation, PermutationGroup
    from sympy.combinatorics.named_groups import SymmetricGroup
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False


# Available permutation ordering types
PERMUTATION_ORDERINGS = ['lex', 'random', 'conjugacy', 'coset']


def generate_permutation_sequences(
    n: int,
    length: Optional[int] = None,
    order: str = 'lex',
    subgroup: Optional[List[Tuple]] = None
) -> List[Tuple]:
    """
    Generate permutation sequences with various orderings using sympy.
    
    This function generates all permutations of S_n (symmetric group on n elements)
    and returns them in a specified order. The permutations are represented as
    tuples using 1-based indexing.
    
    Args:
        n: Degree of symmetric group S_n (acting on {1, 2, ..., n})
        length: Maximum length of sequence (None for all n! elements)
        order: Ordering method:
            - 'lex': Lexicographic (dictionary) order
            - 'random': Randomly shuffled order
            - 'conjugacy': Grouped by conjugacy classes
            - 'coset': Ordered by cosets (requires subgroup parameter)
        subgroup: For coset ordering, list of tuples representing generators
                 of the subgroup H. Permutations will be grouped by left cosets gH.
    
    Returns:
        List of permutation tuples, where each tuple represents a permutation
        using 1-based indexing (e.g., (2, 1, 3) means 1→2, 2→1, 3→3)
    
    Raises:
        ValueError: If order is 'coset' but no subgroup is provided
        ImportError: If sympy is not available for advanced orderings
    
    Example:
        >>> generate_permutation_sequences(3, order='lex')
        [(1, 2, 3), (1, 3, 2), (2, 1, 3), (2, 3, 1), (3, 1, 2), (3, 2, 1)]
        
        >>> generate_permutation_sequences(3, length=3, order='random')
        [(2, 1, 3), (3, 2, 1), (1, 2, 3)]  # Random order
    """
    
    def tuple_to_perm(t: Tuple) -> 'Permutation':
        """Convert 1-based tuple to sympy Permutation (0-based)."""
        return Permutation([x - 1 for x in t])
    
    def perm_to_tuple(p: 'Permutation') -> Tuple:
        """Convert sympy Permutation (0-based) to 1-based tuple."""
        return tuple(x + 1 for x in p.array_form)
    
    # Generate base set and all permutations
    base_set = tuple(range(1, n + 1))
    all_tuples = list(permutations(base_set))
    
    # Apply ordering
    if order == 'lex':
        # Already in lexicographic order from itertools.permutations
        sequences = all_tuples
        
    elif order == 'random':
        # Shuffle the permutations randomly
        random_shuffle(all_tuples)
        sequences = all_tuples
        
    elif order == 'conjugacy':
        # Group by conjugacy classes (requires sympy)
        if not SYMPY_AVAILABLE:
            raise ImportError(
                "sympy is required for conjugacy ordering. "
                "Install with: pip install sympy"
            )
        
        G = SymmetricGroup(n)
        conjugacy_classes = G.conjugacy_classes()
        sequences = []
        for conjugacy_class in conjugacy_classes:
            for perm in conjugacy_class:
                sequences.append(perm_to_tuple(perm))
                
    elif order == 'coset':
        # Order by cosets of a subgroup (requires sympy)
        if not SYMPY_AVAILABLE:
            raise ImportError(
                "sympy is required for coset ordering. "
                "Install with: pip install sympy"
            )
        
        if subgroup is None:
            raise ValueError(
                "For coset ordering, please specify a subgroup parameter. "
                "Example: subgroup=[(1, 2, 3, 4), (2, 1, 4, 3)]"
            )
        
        # Create the group and subgroup
        G = SymmetricGroup(n)
        H = PermutationGroup([tuple_to_perm(h) for h in subgroup])
        
        # Generate all distinct left cosets
        sequences = []
        used_elements = set()
        
        # Use elements from original tuple list to maintain some order
        for g_tuple in all_tuples:
            g = tuple_to_perm(g_tuple)
            if g not in used_elements:
                # Get the entire coset gH
                coset = [g * h for h in H.elements]
                sequences.extend(perm_to_tuple(p) for p in coset)
                used_elements.update(coset)
    else:
        raise ValueError(
            f"Invalid ordering: '{order}'. "
            f"Valid orderings: {PERMUTATION_ORDERINGS}"
        )
    
    # Apply length limit if specified
    return sequences if length is None else sequences[:length]


class GroupPattern(Pattern):
    """
    Group theory-based arpeggio pattern generator.
    
    Uses permutations from symmetric groups to generate unique note orderings.
    Each permutation reorders the chord notes in a different way, creating
    mathematically structured patterns.
    
    This pattern type is particularly useful for:
    - Creating non-repetitive, evolving arpeggios
    - Exploring all possible note orderings systematically
    - Generating patterns with mathematical structure
    
    Attributes:
        n (int): Size of permutation group (typically chord size)
        order (str): Permutation ordering type
        subgroup (List[Tuple]): Subgroup for coset ordering (optional)
    
    Example:
        >>> pattern = GroupPattern(n=3, order='lex')
        >>> # With a 3-note chord, generates all 6 permutations
        >>> pattern.generate(['C4', 'E4', 'G4'])
        ['C4', 'E4', 'G4',   # (1,2,3)
         'C4', 'G4', 'E4',   # (1,3,2)
         'E4', 'C4', 'G4',   # (2,1,3)
         'E4', 'G4', 'C4',   # (2,3,1)
         'G4', 'C4', 'E4',   # (3,1,2)
         'G4', 'E4', 'C4']   # (3,2,1)
    """
    
    def __init__(
        self, 
        n: int = 3, 
        order: str = 'lex',
        subgroup: Optional[List[Tuple]] = None
    ):
        """
        Initialize a GroupPattern with permutation parameters.
        
        Args:
            n: Size of the permutation group S_n. This should typically
               match or exceed the number of notes in the chord.
               Default is 3 (for triads).
            order: How to order the permutations:
                - 'lex': Lexicographic (standard dictionary order)
                - 'random': Random order
                - 'conjugacy': Grouped by conjugacy class
                - 'coset': Ordered by cosets of subgroup
            subgroup: Required if order='coset'. List of permutation tuples
                     that generate the subgroup.
        
        Raises:
            ValueError: If order is not recognized or coset without subgroup.
        """
        if order not in PERMUTATION_ORDERINGS:
            raise ValueError(
                f"Unknown ordering: '{order}'. "
                f"Valid orderings: {PERMUTATION_ORDERINGS}"
            )
        
        if order == 'coset' and subgroup is None:
            raise ValueError(
                "Subgroup parameter required for coset ordering. "
                "Provide a list of permutation tuples."
            )
        
        super().__init__(f'group_{order}')
        self.n = n
        self.order = order
        self.subgroup = subgroup
        self._permutations = None  # Lazy-loaded
    
    def _get_permutations(self) -> List[Tuple]:
        """
        Get or generate the permutation sequences.
        
        Uses lazy loading to avoid computing permutations until needed.
        """
        if self._permutations is None:
            self._permutations = generate_permutation_sequences(
                n=self.n,
                order=self.order,
                subgroup=self.subgroup
            )
        return self._permutations
    
    def generate(
        self, 
        notes: List[Any], 
        count: Optional[int] = None,
        chord_sequence: Optional[List[List[Any]]] = None,
        **kwargs
    ) -> List[Any]:
        """
        Generate a sequence of notes using permutation patterns.
        
        Each permutation from the symmetric group is applied to reorder
        the chord notes. The permutations use 1-based indexing internally
        but are applied to 0-based note lists.
        
        Args:
            notes: List of notes for a single chord, or ignored if
                  chord_sequence is provided.
            count: Maximum number of notes to generate. If None, generates
                  all permutations applied to the notes.
            chord_sequence: Optional list of note lists for progression.
                          Each permutation cycles through the chords.
            **kwargs: Additional parameters (ignored)
        
        Returns:
            List of notes reordered according to permutations.
        
        Example:
            >>> pattern = GroupPattern(n=3, order='lex')
            >>> pattern.generate(['C4', 'E4', 'G4'], count=9)
            ['C4', 'E4', 'G4', 'C4', 'G4', 'E4', 'E4', 'C4', 'G4']
        """
        perms = self._get_permutations()
        
        if not perms:
            # Fallback if no permutations generated
            return notes[:count] if count else notes
        
        # Use chord_sequence if provided, otherwise wrap notes
        if chord_sequence is None:
            chord_sequence = [notes]
        
        num_chords = len(chord_sequence)
        chord_size = len(notes) if notes else len(chord_sequence[0])
        
        result = []
        
        for i, perm in enumerate(perms):
            # Select current chord (cycle through if multiple)
            current_chord = chord_sequence[i % num_chords]
            
            # Apply permutation to chord notes
            # Convert 1-based permutation to 0-based indices
            for p in perm:
                idx = (p - 1) % len(current_chord)
                result.append(current_chord[idx])
            
            # Check if we've generated enough notes
            if count is not None and len(result) >= count:
                break
        
        # Trim to exact count if specified
        if count is not None:
            result = result[:count]
        
        return result
    
    def regenerate(self) -> None:
        """
        Regenerate permutation sequences.
        
        Useful for 'random' ordering to get a new random sequence,
        or to reset after parameter changes.
        """
        self._permutations = None
    
    @classmethod
    def available_orderings(cls) -> List[str]:
        """
        Get list of available permutation orderings.
        
        Returns:
            List of ordering type names.
        """
        return PERMUTATION_ORDERINGS.copy()