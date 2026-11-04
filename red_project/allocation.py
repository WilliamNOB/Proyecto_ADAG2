"""Asignación óptima de unidades de presupuesto con utilidades cóncavas."""

from dataclasses import dataclass
import heapq
import math
from typing import Sequence


@dataclass(frozen=True)
class AllocationResult:
    amounts: tuple[int, ...]
    utility: float


def greedy_allocate(marginals: Sequence[Sequence[float]], budget: int) -> AllocationResult:
    """Asigna cada unidad al mayor marginal disponible.

    ``marginals[i][j]`` es la ganancia de entregar la unidad ``j + 1`` al
    nodo ``i``. La concavidad discreta exige que cada fila no sea creciente.
    """
    if not isinstance(budget, int) or isinstance(budget, bool) or budget < 0:
        raise ValueError("budget debe ser un entero no negativo")
    if any(any(not math.isfinite(value) or value < 0 for value in row)
           for row in marginals):
        raise ValueError("las ganancias deben ser finitas y no negativas")
    if any(any(row[j] < row[j + 1] for j in range(len(row) - 1))
           for row in marginals):
        raise ValueError("cada utilidad debe ser cóncava discreta")

    amounts = [0] * len(marginals)
    heap: list[tuple[float, int, int]] = []
    for node, row in enumerate(marginals):
        if row:
            heapq.heappush(heap, (-row[0], node, 0))

    utility = 0.0
    for _ in range(budget):
        if not heap:
            break
        negative_gain, node, position = heapq.heappop(heap)
        gain = -negative_gain
        amounts[node] += 1
        utility += gain
        next_position = position + 1
        if next_position < len(marginals[node]):
            heapq.heappush(
                heap, (-marginals[node][next_position], node, next_position)
            )
    return AllocationResult(tuple(amounts), utility)


def utility_from_marginals(marginals: Sequence[Sequence[float]],
                           amounts: Sequence[int]) -> float:
    """Calcula la utilidad de una asignación, validando sus límites."""
    if len(marginals) != len(amounts):
        raise ValueError("amounts debe tener una entrada por nodo")
    total = 0.0
    for row, amount in zip(marginals, amounts):
        if (not isinstance(amount, int) or isinstance(amount, bool)
                or amount < 0 or amount > len(row)):
            raise ValueError("cantidad asignada fuera del rango")
        total += sum(row[:amount])
    return total
