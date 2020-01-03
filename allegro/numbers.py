# pyright: strict

"""
numbers.py

The numbers module contains functions and classes that do "numeric"
transformations.
"""
import math
from enum import (
    Enum,
    auto,
)
from functools import partial
from typing import Sequence, TypeVar


class FitMode(Enum):
    """FitMode contains the available modes for the fit function."""

    WRAP = auto()
    CLAMP = auto()


def fit(mode: FitMode, lo: int, hi: int, num: int) -> int:
    """fit transforms a value to "fit" within a range according to a mode.

    args:
    mode -- a FitMode enumeration value.
    lo -- int representing the low end of the range.
    hi -- int representing the high end of the range.
    num -- int to be fit in the range according to the given mode.

    More on FitModes:
    Wrap mode uses modular (aka "clock") arithmetic to "wrap" n into the range.
    This is expressed in the following equation:
        n' = n - floor((n - lo) / (hi - lo)) *  (hi - lo)

    Clamp mode takes any out-of-range values and replaces with the nearest
    bound.
    """
    if lo <= num and num <= hi:
        return num
    else:
        if mode == FitMode.WRAP:
            fit_range = hi - lo
            return num - ((num - lo) // fit_range) * fit_range
        else:
            return hi if num > hi else lo


fit_wrap = partial(fit, FitMode.WRAP)
fit_wrap.__doc__ = "Same as fit function with Wrap passed to mode argument."

fit_clamp = partial(fit, FitMode.CLAMP)
fit_clamp.__doc__ = "Same as fit function with Clamp passed to mode argument."


def deltas(l: Sequence[float]) -> Sequence[float]:
    """deltas returns list of differences between adjacent numbers
    in the input list.

    l -- a list of floats.

    Note, the resulting list will be one element shorter
    than the input list.

    Example:
    In:  [3, 2, 1]
    Out: [1, 1]
    """
    if not l or len(l) == 1:
        return l
    else:
        return [x - y for x, y in zip(l, l[1:])]


class QuantizeMode(Enum):
    MIDTREAD = auto()
    MIDRISER = auto()


TNum = TypeVar("TNum", int, float)


def quantize(mode: QuantizeMode, step: TNum, num: TNum) -> TNum:
    """quantize transforms a number to the closest multiple of step.

    mode -- a quantize mode of type QuantizeMode.
    step -- a step (or grid) value that num will be fit to of type TNum.
    num -- a num of type TNum.

    There are two modes:
    MidTread uses the following algorithm:
        step * floor((n / step) + 0.5)
    MidRiser uses the following algorithm:
        step * (floor(n / step)) + 0.5
    """

    if mode == QuantizeMode.MIDTREAD:
        classifier = math.floor((num / step) + 0.5)
        return step * classifier
    else:
        classifier = math.floor(num / step)
        return step * (classifier + 0.5)


midtread_quantize = partial(quantize, QuantizeMode.MIDTREAD)
midtread_quantize.__doc__ = "Same as quantize function \
    with MIDTREAD passed to mode."

midriser_quantize = partial(quantize, QuantizeMode.MIDRISER)
midriser_quantize.__doc__ = "Same as quantize function \
    with MIDRISER passed to mode."
