from itertools import permutations
from random import shuffle
from sympy.combinatorics import Permutation, PermutationGroup
from sympy.combinatorics.named_groups import SymmetricGroup


def generate_permutation_sequences(n, length=None, order='lex', subgroup=None):
    """
    Generate permutation sequences as tuples with various orderings using sympy.

    Parameters:
    - n: Degree of symmetric group S_n (acting on {1,2,...,n})
    - length: Maximum length of sequence (None for all n! elements)
    - order: Ordering method:
        'lex' - lexicographic (default)
        'random' - random order
        'conjugacy' - group by conjugacy classes
        'coset' - ordered by cosets (requires subgroup)
    - subgroup: For coset ordering, list of tuples representing subgroup
    """

    # Convert between tuple and sympy permutation representations
    def tuple_to_perm(t):
        return Permutation([x - 1 for x in t])  # sympy uses 0-based

    def perm_to_tuple(p):
        return tuple(x + 1 for x in p.array_form)  # convert back to 1-based

    base_set = tuple(range(1, n + 1))
    all_tuples = list(permutations(base_set))

    if order == 'lex':
        sequences = all_tuples
    elif order == 'random':
        shuffle(all_tuples)
        sequences = all_tuples
    elif order == 'conjugacy':
        G = SymmetricGroup(n)
        conjugacy_classes = G.conjugacy_classes()
        sequences = []
        for c in conjugacy_classes:
            for perm in c:
                sequences.append(perm_to_tuple(perm))
    elif order == 'coset':
        if subgroup is None:
            raise ValueError("For coset ordering, please specify a subgroup")

        # Create the group and subgroup
        G = SymmetricGroup(n)
        H = PermutationGroup([tuple_to_perm(h) for h in subgroup])

        # Generate all distinct left cosets
        sequences = []
        used_elements = set()

        # We'll use the elements from our original tuple list to maintain order
        for g_tuple in all_tuples:
            g = tuple_to_perm(g_tuple)
            if g not in used_elements:
                # Get the entire coset gH
                coset = [g * h for h in H.elements]
                sequences.extend(perm_to_tuple(p) for p in coset)
                used_elements.update(coset)
    else:
        raise ValueError(f"Invalid ordering: {order}")

    return sequences if length is None else sequences[:length]


# Example usage:
if __name__ == "__main__":
    # S3 by conjugacy classes
    print("S3 ordered by conjugacy classes:")
    for p in generate_permutation_sequences(3, order='conjugacy'):
        print(p)

    # S4 by cosets of Klein 4-group
    klein4 = [(1, 2, 3, 4), (1, 2, 4, 3), (1, 3, 2, 4), (1, 3, 4, 2)]  # Klein 4 subgroup
    print("\nS4 ordered by cosets of Klein 4-group (first 12 elements):")
    s4_coset = generate_permutation_sequences(4, order='coset', subgroup=klein4)
    for i, p in enumerate(s4_coset[:12], 1):
        print(f"{i:2}: {p}")

    # Verify we get all 24 elements of S4
    print(f"\nTotal elements generated: {len(s4_coset)} (should be 24 for S4)")
    import pandas as pd
    import numpy as np
    from itertools import permutations
    from sympy.combinatorics import Permutation, SymmetricGroup, PermutationGroup
    from random import shuffle


    # Test the function
    def test_permutation_sequences():
        # Test parameters
        n = 4  # Using S_4 (4! = 24 permutations, reasonable size for testing)
        length = 100  # Request 100 sequences
        subgroup = [(1, 2, 3, 4), (1, 2)]  # Example subgroup for coset ordering

        # Test all ordering types
        orderings = ['lex', 'random', 'conjugacy', 'coset']
        results = {}

        for order in orderings:
            print(f"\nTesting order: {order}")
            try:
                # Generate sequences
                sequences = generate_permutation_sequences(
                    n=n,
                    length=length,
                    order=order,
                    subgroup=subgroup if order == 'coset' else None
                )

                # Store in results
                results[order] = sequences

                # Print some basic info
                print(f"Generated {len(sequences)} sequences")
                print(f"First 5 sequences: {sequences[:5]}")

                # Verify uniqueness if length <= 24 (since S_4 has 24 elements)
                if len(sequences) <= 24:
                    unique_sequences = len(set(sequences))
                    print(f"Unique sequences: {unique_sequences}")
                    assert unique_sequences == len(sequences), "Duplicate sequences found!"

            except Exception as e:
                print(f"Error in {order} ordering: {str(e)}")

        # Create DataFrame
        # We'll store each ordering type in separate columns
        max_length = max(len(seq) for seq in results.values())
        df_data = {}

        for order, sequences in results.items():
            # Pad sequences if necessary
            padded_sequences = sequences + [(None,) * n] * (max_length - len(sequences))
            df_data[f'{order}_perm'] = padded_sequences

        df = pd.DataFrame(df_data)

        # Save to CSV
        df.to_csv('permutation_sequences.csv', index=False)
        print("\nResults saved to 'permutation_sequences.csv'")

        # Display basic DataFrame info
        print("\nDataFrame Info:")
        print(df.info())
        print("\nFirst few rows:")
        print(df.head())

        return df


    # Run the test
    df = test_permutation_sequences()

