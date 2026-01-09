from midimaxgen import Arpeggiator

arp = Arpeggiator(key='C', octave=4, bpm=120)

# Use conjugacy class ordering for structured mathematical patterns
arp.generate_arpeggio(
    progression=[6, 5, 4, 6],
    durations=[1, 1, 1, 1],
    pattern='group',
    order='conjugacy',
    notes_per_chord=8,
    permutation_size=8  # S_4 has 24 permutations
)
arp.save('math_arpeggio.mid')
