"""
iterables.py

Functions for working with iterables.
"""
from typing import Iterable, T, Tuple
from itertools import tee, chain, islice


def current_with_next(iterable: Iterable[T]) -> Iterable[Tuple[T, T]]:
    currents, nexts = tee(iterable, 2)
    nexts = chain(islice(nexts, 1, None), [None])
    return zip(currents, nexts)
