from permutations import *


def create_symmetric_group_of_order(n) -> list[Permutation]:
    if n == 1:
        return [E]
    else:
        S = create_symmetric_group_of_order(n - 1)
        return S + [(x * Cycle(n, i)).to_minimal_form() for x in S for i in range(1, n)]



if __name__ == "__main__":

    # example:
    S5 = create_symmetric_group_of_order(5)
    A5 = [f for f in S5 if len(f.to_transpositions().cycles) % 2 == 0]
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
