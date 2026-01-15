from midimaxgen import Arpeggiator

arp = Arpeggiator(key='C', octave=4, bpm=120)

# arp.generate_arpeggio(
#     progression=[6, 5, 4, 6],
#     durations=[1, 1, 1, 1],
#     pattern='group',
#     order='coset',
#     subgroup=[(1, 2, 3, 4), (2, 1, 4, 3)],
#     notes_per_chord=4,
#     permutation_size=8  # S_4 has 24 permutations
# )
# arp.save('subgroup_coset_arpeggio.mid')

arp.generate_arpeggio(
    progression=(6, 5, 4, 6),
    durations=[1, 1, 1, 1], 
    pattern='group',
    order='conjugacy',
    note_duration=0.25,
    permutation_size=4
)

arp.save('viz_ex_002.mid')