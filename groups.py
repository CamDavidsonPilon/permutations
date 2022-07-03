from __future__ import annotations
from permutations import *
from itertools import combinations

class Vector(list):
    def __mul__(self, other) -> Vector:
        return Vector([(s * o).to_minimal_form() for (s, o) in zip(self, other)])



def create_symmetric_group_of_order(n) -> PermutationCollection:
    if n == 1:
        return PermutationCollection([E])
    else:
        S = create_symmetric_group_of_order(n - 1)
        return S + PermutationCollection((x * Cycle(n, i)).to_minimal_form() for x in S for i in range(1, n) )

def create_alternating_group_of_order(n) -> PermutationCollection:
    return PermutationCollection(f for f in create_symmetric_group_of_order(n) if f.parity == 0)


def create_isomorphic_cycle_group_of_order(n) -> PermutationCollection:
    generator = Cycle(*range(1, n+1))
    return PermutationCollection([generator**i for i in range(n)])




def is_group(collection: PermutationCollection):
    if E not in collection:
        return False

    for (i, j) in combinations(collection, 2):
        # this assume commutativity
        if i * j not in collection:
            return False

        if (i.inverse() not in collection) or (j.inverse() not in collection):
            return False

    return True


def all_subgroups_of_group(known_group):
    known_group = copy(known_group)
    n = len(known_group)
    # pop out E, will add later
    known_group.remove(E)

    yield PermutationCollection([E])

    for i in range(2, n-1):
        if n % i != 0:
            continue
        for naked_collection_ in combinations(known_group, i-1):
            collection_ = PermutationCollection(naked_collection_ + (E,))
            if is_group(collection_):
                yield collection_



if __name__ == "__main__":

    # example:
    S5 = list(create_symmetric_group_of_order(5))
    assert (S5[4] * S5[10] * S5[11]) in S5

    A5 = list(create_alternating_group_of_order(5))
    assert (A5[1] * A5[5]) in A5

    # the two generators of the sporadic group M24.
    G1 = Permutation(
        Cycle(1, 16, 8, 23, 13, 14, 5),
        Cycle(2, 7, 11, 19, 20, 24, 12),
        Cycle(3, 4, 17, 9, 22, 21, 15),
    )

    G2 = Permutation(
        Cycle(1, 24),
        Cycle(2, 21),
        Cycle(3, 10),
        Cycle(4, 22),
        Cycle(5, 9),
        Cycle(6, 23),
        Cycle(7, 8),
        Cycle(11, 18),
        Cycle(12, 20),
        Cycle(13, 14),
        Cycle(15, 19),
        Cycle(16, 17),
    )

    (G1**2 * G2 * G1 **2 * G2 ** 2).to_minimal_form() # another member of M24.
