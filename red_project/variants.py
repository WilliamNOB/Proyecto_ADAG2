"""Variantes obligatorias: fallos entre rondas y externalidades de vecinos."""

from dataclasses import dataclass
import math
import random
from typing import Sequence

from .selection import SelectionResult, SetUtility, greedy_select


@dataclass(frozen=True)
class RoundResult:
    rounds: tuple[SelectionResult, ...]
    total_utility: float


def select_over_rounds(node_count: int, k: int, rounds: int,
                       utility: SetUtility, failure_probability: float,
                       seed: int = 0) -> RoundResult:
    """Selecciona en cada ronda, retirando nodos que fallan entre rondas."""
    if (not isinstance(rounds, int) or isinstance(rounds, bool) or rounds < 0
            or not math.isfinite(failure_probability)
            or not 0 <= failure_probability <= 1):
        raise ValueError("rondas y probabilidad de fallo no son válidas")
    rng = random.Random(seed)
    active = set(range(node_count))
    results: list[SelectionResult] = []
    for _ in range(rounds):
        available = sorted(active)
        local_utility = lambda chosen, available=available: utility(
            frozenset(available[index] for index in chosen)
        )
        local = greedy_select(len(available), min(k, len(available)),
                              local_utility)
        selected = tuple(available[index] for index in local.selected)
        result = SelectionResult(selected, utility(frozenset(selected)))
        results.append(result)
        active.difference_update(
            node for node in tuple(active) if rng.random() < failure_probability
        )
    return RoundResult(tuple(results), sum(item.utility for item in results))


def neighborhood_utility(base_utility: SetUtility,
                         neighbors: Sequence[set[int]],
                         influence: float) -> SetUtility:
    """Añade una penalización/beneficio por vecinos de los seleccionados."""
    if (len(neighbors) == 0 or any(
            node < 0 or node >= len(neighbors)
            for adjacency in neighbors for node in adjacency
    ) or not math.isfinite(influence) or influence < 0):
        raise ValueError("vecindario e influencia no son válidos")

    def utility(selected: frozenset[int]) -> float:
        value = base_utility(selected)
        affected = {neighbor for node in selected for neighbor in neighbors[node]}
        return value + influence * len(affected)
    return utility
