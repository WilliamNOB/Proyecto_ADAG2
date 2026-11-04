"""Instancias sintéticas y medición reproducible de crecimiento."""

from __future__ import annotations

import csv
import random
import statistics
import time
from pathlib import Path

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
        "seed": seed,
    }


def run_experiment(output: Path, sizes: list[int] | None = None,
                   repetitions: int = 20) -> Path:
    if repetitions < 1:
        raise ValueError("repetitions debe ser positivo")
    sizes = sizes or [8, 10, 12, 14, 16]
    output.mkdir(parents=True, exist_ok=True)
    rows = [
        measure(size, max(1, size // 3), seed=size * 1000 + repetition)
        for size in sizes
        for repetition in range(repetitions)
    ]
    csv_path = output / "times.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    summary = _summarize(rows)
    summary_path = output / "summary.csv"
    with summary_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=summary[0].keys())
        writer.writeheader()
        writer.writerows(summary)
    _plot(summary, output / "times.png", "greedy_seconds", "exact_seconds",
          "Tiempo promedio (s)", "Crecimiento experimental del tiempo")
    _plot(summary, output / "approximation.png", "ratio_mean", None,
          "Razón greedy / óptimo", "Calidad promedio de la aproximación")
    return csv_path


def _summarize(rows: list[dict[str, float | int]]) -> list[dict[str, float | int]]:
    summary = []
    for node_count in sorted({row["n"] for row in rows}):
        group = [row for row in rows if row["n"] == node_count]
        summary.append({
            "n": node_count,
            "k": group[0]["k"],
            "repetitions": len(group),
            "greedy_seconds": statistics.mean(row["greedy_seconds"] for row in group),
            "greedy_seconds_std": statistics.stdev(
                row["greedy_seconds"] for row in group
            ) if len(group) > 1 else 0.0,
            "exact_seconds": statistics.mean(row["exact_seconds"] for row in group),
            "exact_seconds_std": statistics.stdev(
                row["exact_seconds"] for row in group
            ) if len(group) > 1 else 0.0,
            "ratio_mean": statistics.mean(row["approximation_ratio"] for row in group),
            "ratio_std": statistics.stdev(
                row["approximation_ratio"] for row in group
            ) if len(group) > 1 else 0.0,
        })
    return summary


def _plot(rows: list[dict[str, float | int]], path: Path,
          primary: str, secondary: str | None, ylabel: str, title: str) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return
    x = [row["n"] for row in rows]
    primary_std = "ratio_std" if primary == "ratio_mean" else f"{primary}_std"
    plt.errorbar(
        x, [row[primary] for row in rows],
        yerr=[row[primary_std] for row in rows],
        fmt="o-", label="Greedy O(Nk)" if secondary else "Greedy / óptimo",
    )
    if secondary:
        plt.errorbar(
            x, [row[secondary] for row in rows],
            yerr=[row[f"{secondary}_std"] for row in rows],
            fmt="o-", label="Exact",
        )
    plt.xlabel("N (número de nodos)")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
