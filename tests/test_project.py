import unittest
import math

from red_project.allocation import greedy_allocate, utility_from_marginals
from red_project.selection import (brute_force_select, greedy_budgeted_select,
                                    greedy_select, maximum_coverage_utility)
from red_project.variants import (neighborhood_utility, select_over_rounds)


class ProjectTests(unittest.TestCase):
    def test_allocation_is_optimal(self):
        marginals = [[8, 6, 3], [7, 5, 1], [4, 4, 2]]
        result = greedy_allocate(marginals, 5)
        self.assertEqual(result.amounts, (2, 2, 1))
        self.assertEqual(result.utility, utility_from_marginals(
            marginals, result.amounts))

    def test_allocation_boundary_and_validation(self):
        marginals = [[3, 2], [1]]
        self.assertEqual(greedy_allocate(marginals, 0).amounts, (0, 0))
        self.assertEqual(greedy_allocate(marginals, 10).amounts, (2, 1))
        with self.assertRaises(ValueError):
            greedy_allocate([[1, math.inf]], 1)
        with self.assertRaises(ValueError):
            greedy_allocate([[1, 2]], 1)

    def test_greedy_matches_exact_on_small_coverage(self):
        coverage = [{0, 1, 2}, {2, 3}, {1, 3, 4}, {0, 4}]
        utility = maximum_coverage_utility(coverage)
        exact = brute_force_select(4, 2, utility)
        greedy = greedy_select(4, 2, utility)
        self.assertEqual(greedy.utility, exact.utility)

    def test_budgeted_selection_is_feasible(self):
        coverage = [{0, 1}, {2, 3, 4}, {0, 4}]
        result = greedy_budgeted_select(coverage, [1, 3, 2], 3)
        self.assertLessEqual(sum([1, 3, 2][i] for i in result.selected), 3)
        with self.assertRaises(ValueError):
            greedy_budgeted_select(coverage, [1, math.inf, 2], 3)
        with self.assertRaises(ValueError):
            greedy_budgeted_select(coverage, [1, 2, 3], math.inf)

    def test_zero_cardinality_selection(self):
        utility = maximum_coverage_utility([{0}, {1}])
        self.assertEqual(greedy_select(2, 0, utility).selected, ())
        self.assertEqual(brute_force_select(2, 0, utility).selected, ())

    def test_round_failures_and_reproducibility(self):
        utility = maximum_coverage_utility([{0}, {1}, {2}])
        no_failures = select_over_rounds(3, 2, 2, utility, 0, seed=10)
        self.assertEqual(no_failures.rounds[0].selected,
                         no_failures.rounds[1].selected)
        all_failures = select_over_rounds(3, 2, 2, utility, 1, seed=10)
        self.assertEqual(all_failures.rounds[1].selected, ())
        first = select_over_rounds(3, 2, 3, utility, 0.4, seed=4)
        second = select_over_rounds(3, 2, 3, utility, 0.4, seed=4)
        self.assertEqual(first, second)

    def test_neighborhood_influence_includes_selected_neighbors(self):
        base = maximum_coverage_utility([{0}, {1}])
        utility = neighborhood_utility(base, [{1}, {0}], 2)
        self.assertEqual(utility(frozenset({0, 1})), 6.0)


if __name__ == "__main__":
    unittest.main()
