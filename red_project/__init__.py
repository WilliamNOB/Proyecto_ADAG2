"""Algoritmos del proyecto de optimización de la Red."""

from .allocation import AllocationResult, greedy_allocate
from .selection import SelectionResult, brute_force_select, greedy_select

__all__ = [
    "AllocationResult",
    "SelectionResult",
    "brute_force_select",
    "greedy_allocate",
    "greedy_select",
]
