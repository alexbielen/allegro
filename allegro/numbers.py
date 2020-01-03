# pyright: strict

"""
numbers.py

The numbers module contains functions and classes that do "numeric"
transformations.
"""
from enum import (
    Enum,
    auto,
)
from functools import partial


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
