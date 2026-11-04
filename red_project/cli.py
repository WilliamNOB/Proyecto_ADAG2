"""Interfaz de ejecución para demostraciones y experimentos."""

import argparse
from pathlib import Path

from .allocation import greedy_allocate
from .experiments import run_experiment
from .selection import (brute_force_select, greedy_select,
                        maximum_coverage_utility)


def main() -> None:
    parser = argparse.ArgumentParser(description="Proyecto Red")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("demo")
    experiment = subparsers.add_parser("experiment")
    experiment.add_argument("--output", type=Path, default=Path("results"))
    experiment.add_argument("--repetitions", type=int, default=20)
    args = parser.parse_args()
    if args.command == "demo":
        allocation = greedy_allocate(
            [[8, 6, 3], [7, 5, 1], [4, 4, 2]], budget=5
        )
        coverage = [{0, 1, 2}, {2, 3}, {1, 3, 4}, {0, 4}]
        utility = maximum_coverage_utility(coverage)
        print("Asignación:", allocation)
        print("Selección greedy:", greedy_select(4, 2, utility))
        print("Óptimo exacto:", brute_force_select(4, 2, utility))
    else:
        print(f"Resultados escritos en {run_experiment(args.output, repetitions=args.repetitions)}")


if __name__ == "__main__":
    main()
