from __future__ import annotations
from collections.abc import MutableSequence
from copy import copy
from typing import Union, Literal
from math import lcm
from functools import reduce
from operator import xor


class PermutationCollection(set):

    def __mul__(self, other):
        if isinstance(other, (Permutation, Cycle)):
            # List * permutation
            return PermutationCollection(( (f * other).to_minimal_form() for f in self))
        else:
            raise ValueError

    def __add__(self, other):
        return PermutationCollection(self.union(other))



class Permutation:
    def __init__(self, *cycles: Union[Permutation, Cycle]):
        self.cycles = cycles

    def __call__(self, indexable_or_int: MutableSequence | int) -> MutableSequence | int:
        indexable_or_int = copy(indexable_or_int)

        for cycle in reversed(self.cycles):
            indexable_or_int = cycle(indexable_or_int)

        return indexable_or_int

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

    def __mul__(self, other: Union[Permutation, Cycle, PermutationCollection]):
        if isinstance(other, Cycle):
            return Permutation(*self.cycles, other)
        elif isinstance(other, PermutationCollection):
            return PermutationCollection(( (self * f).to_minimal_form() for f in other))
        else:
            return Permutation(*self.cycles, *other.cycles).to_minimal_form()

    def __pow__(self, exponent: int):
        P = E
        for _ in range(exponent):
            P = P * self
        return P.to_minimal_form()

    def inverse(self) -> Permutation:
        # group inverse, so that P(P.inverse()(L)) == L == P.inverse()(P(L))
        return Permutation(*(c.inverse() for c in reversed(self.cycles))).to_minimal_form()

    def __eq__(self, other):
        if isinstance(other, Cycle):
            return len(self.cycles) == 1 and (self.cycles[0] == Cycle)
        else:
            if self.is_minimal_form and other.is_minimal_form:
                return hash(self) == hash(other)
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

    @property
    def is_minimal_form(self) -> bool:
        # is in increasing cycle order, and no overlap?
        if hasattr(self, "_is_minimal_form"):
            return self._is_minimal_form

        seen = set([])
        min_ = 0
        for c in self.cycles:
            if c.is_minimal_form:
                if seen.intersection(c._indexes_touched) or min(c._indexes_touched) >= min_:
                    self._is_minimal_form = False
                    return self._is_minimal_form
                seen = seen.union(c._indexes_touched)
                min_ = min(c._indexes_touched)

            else:
                self._is_minimal_form = False
                return self._is_minimal_form
        self._is_minimal_form = True
        return self._is_minimal_form

    def to_minimal_form(self) -> Permutation:
        # find the smallest, disjoint, representation
        # Ex: P = (3, 4)(6, 10)(10, 11)(1, 5)(5, 12)
        # minimal form is (1, 5, 12)(3, 4)(6, 10, 11)

        # this basically sends a number through, and determines where it ends up. Kinda sketch and slow.

        if self.is_minimal_form:
            return self


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

        p = Permutation(*cycles)
        p._is_minimal_form = True
        return p

    @property
    def parity(self) -> Literal[0, 1]:
        running_sum = 0
        for c in self.cycles:
            running_sum += c.parity
        return running_sum % 2


    @property
    def order(self) -> int:
        return lcm(*(c.order for c in self.cycles))


    def __hash__(self) -> int:
        if len(self.cycles) == 0:
            return 1

        if self.is_minimal_form:
            return reduce(xor, map(hash, self.cycles))
        else:
            return hash(self.to_minimal_form())

    @property
    def _indexes_touched(self):
        return reduce(set.union, (c._indexes_touched for c in self.cycles))


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

    @property
    def _indexes_touched(self):
        return set(self.cycle)

    @staticmethod
    def _rotate(l):
        return l[1:] + l[:1]

    def __call__(self, indexable_or_int: MutableSequence | int) -> MutableSequence | int:

        if isinstance(indexable_or_int, int):
            int_ = indexable_or_int
            if int_ in self.cycle:
                ix = self.cycle.index(int_)
                return self.cycle[(ix+1) % self.order]
            else:
                return int_

        else:
            indexable = copy(indexable_or_int)

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
        return f"Cycle{self.cycle}"

    def __mul__(self, other: Union[Permutation, Cycle, PermutationCollection]) -> Permutation:
        if isinstance(other, PermutationCollection):
            return PermutationCollection(( (self * f).to_minimal_form() for f in other))
        else:
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

    @property
    def parity(self) -> Literal[0, 1]:
        return (self.order + 1) % 2

    def to_minimal_form(self) -> Permutation:
        return Permutation(self)

    def __hash__(self):
        return self.cycle.__hash__()

    @property
    def is_minimal_form(self) -> bool:
        return True


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
