from permutations import *


def create_symmetric_group_of_order(n) -> list[Permutations]:
    if n == 1:
        return [E]
    else:
        S = create_symmetric_group_of_order(n-1)
        return S + [
            (x * Cycle(n, i)).to_minimal_form() for x in S
                            for i in range(1, n)
        ]
