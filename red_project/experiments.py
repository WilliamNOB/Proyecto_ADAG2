"""Instancias sintéticas y medición reproducible de crecimiento."""

from __future__ import annotations

import csv
import random
import time
from pathlib import Path
from typing import Callable

from .selection import (brute_force_select, greedy_select,
                        maximum_coverage_utility)


def make_coverage(node_count: int, universe_size: int,
                  seed: int) -> list[set[int]]:
    rng = random.Random(seed)
    return [
        {element for element in range(universe_size) if rng.random() < 0.2}
        for _ in range(node_count)
    ]


def measure(node_count: int, k: int, seed: int = 0) -> dict[str, float | int]:
    coverage = make_coverage(node_count, node_count * 2, seed)
    utility = maximum_coverage_utility(coverage)
    start = time.perf_counter()
    greedy = greedy_select(node_count, k, utility)
    greedy_seconds = time.perf_counter() - start
    start = time.perf_counter()
    exact = brute_force_select(node_count, k, utility)
    exact_seconds = time.perf_counter() - start
    ratio = greedy.utility / exact.utility if exact.utility else 1.0
    return {
        "n": node_count, "k": k, "greedy_seconds": greedy_seconds,
        "exact_seconds": exact_seconds, "greedy_utility": greedy.utility,
        "exact_utility": exact.utility, "approximation_ratio": ratio,
    }


def run_experiment(output: Path, sizes: list[int] | None = None) -> Path:
    sizes = sizes or [8, 10, 12, 14, 16]
    output.mkdir(parents=True, exist_ok=True)
    rows = [measure(size, max(1, size // 3), seed=size) for size in sizes]
    csv_path = output / "times.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    _plot(rows, output / "times.png")
    return csv_path


def _plot(rows: list[dict[str, float | int]], path: Path) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return
    x = [row["n"] for row in rows]
    plt.plot(x, [row["greedy_seconds"] for row in rows], "o-", label="Greedy O(Nk)")
    plt.plot(x, [row["exact_seconds"] for row in rows], "o-", label="Exact")
    plt.xlabel("N (número de nodos)")
    plt.ylabel("Tiempo (s)")
    plt.title("Crecimiento experimental")
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
