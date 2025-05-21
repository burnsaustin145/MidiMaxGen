import pandas as pd
import numpy as np
from itertools import permutations
from sympy.combinatorics import Permutation, SymmetricGroup, PermutationGroup
from random import shuffle
from group_gen import generate_permutation_sequences


# Test the function
def permutation_sequences():
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
df = permutation_sequences()