from __future__ import annotations
from collections.abc import MutableSequence
from copy import copy
from typing import Union


class Permutation:
    def __init__(self, *cycles: Union[Permutation, Cycle]):
        self.cycles = cycles

    def __call__(self, indexable: MutableSequence) -> MutableSequence:
        indexable = copy(indexable)

        for cycle in reversed(self.cycles):
            indexable = cycle(indexable)

        return indexable

    def __str__(self):
        s = ""
        for cycle in self.cycles:
            s += str(cycle)

        if s:
            return s
        else:
            return "E"

    def __repr__(self):
        return str(self)

    def __mul__(self, other: Union[Permutation, Cycle]) -> Permutation:
        if isinstance(other, Cycle):
            return Permutation(*self.cycles, other)
        else:
            return Permutation(*self.cycles, *other.cycles)

    def __pow__(self, exponent: int):
        P = E
        for _ in range(exponent):
            P = P * self
        return P.to_minimal_form()

    def inverse(self) -> Permutation:
        # group inverse, so that P(P.inverse()(L)) == L == P.inverse()(P(L))
        return Permutation(*(c.inverse() for c in reversed(self.cycles)))

    def __eq__(self, other):
        if isinstance(other, Cycle):
            return len(self.cycles) == 1 and (self.cycles[0] == Cycle)
        else:
            return all(
                x == y
                for (x, y) in zip(
                    self.to_minimal_form().cycles, other.to_minimal_form().cycles
                )
            ) and (
                len(self.to_minimal_form().cycles)
                == len(other.to_minimal_form().cycles)
            )

    def max(self) -> int:
        # return the maximum index in the permutation

        if len(self.cycles) == 0:
            return 0
        else:
            return max(map(lambda c: c.max(), self.cycles))

    def to_transpositions(self) -> Permutation:
        # To simple 2-length cycles, not necessarily disjoint
        return Permutation(
            *(t for cycle in self.cycles for t in cycle.to_transpositions().cycles)
        )

    def to_minimal_form(self) -> Permutation:
        # find the smallest, disjoint, representation
        # Ex: P = (3, 4)(6, 10)(10, 11)(1, 5)(5, 12)
        # minimal form is (1, 5, 12)(3, 4)(6, 10, 11)

        # this basically sends a number through, and determines where it ends up. Kinda sketch.

        L = list(range(1, self.max() + 1))
        L_mask = [True] * len(L)
        L_prime = self(L)

        cycles = []
        for i in L:
            if not L_mask[i - 1]:
                continue
            L_mask[i - 1] = False
            cycle = [i]
            j = L_prime.index(i) + 1
            while i != j:
                cycle.append(j)
                L_mask[j - 1] = False
                j = L_prime.index(j) + 1

            if len(cycle) >= 2:
                cycles.append(Cycle(*cycle))

        return Permutation(*cycles)


E = Permutation()  # identity


class Cycle:
    def __init__(self, *args: int):
        assert len(args) >= 2
        assert min(args) >= 1

        # rotate args until the maximum value is first
        m = min(args)

        while args[0] != m:
            args = self._rotate(args)

        self.cycle = args

    @staticmethod
    def _rotate(l):
        return l[1:] + l[:1]

    def __call__(self, indexable: MutableSequence) -> MutableSequence:
        indexable = copy(indexable)

        if self.order == 2:
            a, b = self.cycle
            alpha, beta = indexable[a - 1], indexable[b - 1]  # we use 1-indexing
            indexable[b - 1] = alpha
            indexable[a - 1] = beta
            return indexable
        else:
            p = self.to_transpositions()
            return p(indexable)

    def __str__(self):
        return str(self.cycle)

    def __repr__(self):
        return str(self)

    def __mul__(self, other: Union[Permutation, Cycle]) -> Permutation:
        return Permutation(self, other)

    def __eq__(self, other):
        if isinstance(other, Cycle):
            return self.cycle == other.cycle
        else:
            return other == self

    def __pow__(self, exponent: int):
        return Permutation(self) ** exponent

    def inverse(self) -> Cycle:
        return Cycle(*reversed(self.cycle))

    def to_transpositions(self) -> Permutation:
        if self.order == 2:
            return Permutation(self)
        else:
            a, b, *rest = self.cycle
            return Permutation(Cycle(a, b), *Cycle(b, *rest).to_transpositions().cycles)

    def max(self) -> int:
        return max(self.cycle)

    def min(self) -> int:
        return min(self.cycle)

    @property
    def order(self) -> int:
        return len(self.cycle)

    def to_minimal_form(self):
        return Permutation(self)


if __name__ == "__main__":

    c = Cycle(2, 3)
    assert c(["a", "b", "c", "d"]) == ["a", "c", "b", "d"]

    p = Permutation(Cycle(2, 3), Cycle(1, 3))
    assert p(["a", "b", "c", "d"]) == ["c", "a", "b", "d"]

    c = Cycle(1, 2, 3, 4)
    assert c(["a", "b", "c", "d"]) == ["d", "a", "b", "c"]
    assert Cycle(1, 2, 3, 4) == Cycle(2, 3, 4, 1)

    L = list(range(1, 16))
    P = Permutation(Cycle(3, 4), Cycle(6, 10, 11), Cycle(1, 5, 12))
    print(P)
    print(P.to_transpositions())

    Pinv = P.inverse()
    assert Pinv(P(L)) == L

    assert (Pinv * P) == E == (P * Pinv)

    assert P * E == P
    assert E * P == P
