"""Selección exacta y aproximada de participantes."""

from dataclasses import dataclass
from itertools import combinations
import math
from typing import Callable, Sequence

SetUtility = Callable[[frozenset[int]], float]


@dataclass(frozen=True)
class SelectionResult:
    selected: tuple[int, ...]
    utility: float


def _validate_nodes(node_count: int, k: int) -> None:
    if node_count < 0 or not 0 <= k <= node_count:
        raise ValueError("se requiere 0 <= k <= node_count")


def brute_force_select(node_count: int, k: int,
                       utility: SetUtility) -> SelectionResult:
    """Encuentra el óptimo enumerando todos los subconjuntos de tamaño k."""
    _validate_nodes(node_count, k)
    best = SelectionResult((), float("-inf"))
    for candidate in combinations(range(node_count), k):
        value = utility(frozenset(candidate))
        if value > best.utility:
            best = SelectionResult(candidate, value)
    return best


def greedy_select(node_count: int, k: int,
                  utility: SetUtility) -> SelectionResult:
    """Greedy por ganancia marginal; O(N*k) evaluaciones de la función."""
    _validate_nodes(node_count, k)
    selected: set[int] = set()
    current = utility(frozenset())
    for _ in range(k):
        best_node: int | None = None
        best_value = float("-inf")
        for node in range(node_count):
            if node in selected:
                continue
            value = utility(frozenset(selected | {node}))
            if value - current > best_value:
                best_node, best_value = node, value - current
        if best_node is None:
            break
        selected.add(best_node)
        current += best_value
    return SelectionResult(tuple(sorted(selected)), current)


def maximum_coverage_utility(coverage: Sequence[set[int]]) -> SetUtility:
    """Construye la función submodular |unión de coberturas|."""
    def utility(selected: frozenset[int]) -> float:
        covered: set[int] = set()
        for node in selected:
            covered.update(coverage[node])
        return float(len(covered))
    return utility


def greedy_budgeted_select(coverage: Sequence[set[int]],
                           costs: Sequence[float],
                           budget: float) -> SelectionResult:
    """Greedy por densidad marginal para cobertura con presupuesto.

    La garantía clásica de ``1 - 1/e`` requiere la variante budgeted maximum
    coverage con el tratamiento adecuado del mejor elemento individual. Esta
    función devuelve el mejor entre esa solución greedy y el mejor nodo
    factible, haciendo explícita esa salvaguarda.
    """
    if (len(coverage) != len(costs) or not math.isfinite(budget)
            or budget < 0):
        raise ValueError("cobertura, costos y presupuesto son incompatibles")
    if any(not math.isfinite(cost) or cost <= 0 for cost in costs):
        raise ValueError("cada costo debe ser finito y positivo")
    selected: set[int] = set()
    covered: set[int] = set()
    spent = 0.0
    while True:
        candidates = [
            node for node in range(len(coverage))
            if node not in selected and spent + costs[node] <= budget
        ]
        if not candidates:
            break
        node = max(
            candidates,
            key=lambda item: (len(coverage[item] - covered) / costs[item],
                              -item),
        )
        gain = len(coverage[node] - covered)
        if gain == 0:
            break
        selected.add(node)
        covered.update(coverage[node])
        spent += costs[node]

    greedy = SelectionResult(tuple(sorted(selected)), float(len(covered)))
    singles = [
        SelectionResult((node,), float(len(coverage[node])))
        for node in range(len(coverage)) if costs[node] <= budget
    ]
    return max([greedy, *singles], key=lambda result: result.utility,
               default=SelectionResult((), 0.0))
