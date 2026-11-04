import unittest

from red_project.allocation import greedy_allocate, utility_from_marginals
from red_project.selection import (brute_force_select, greedy_budgeted_select,
                                    greedy_select, maximum_coverage_utility)


class ProjectTests(unittest.TestCase):
    def test_allocation_is_optimal(self):
        marginals = [[8, 6, 3], [7, 5, 1], [4, 4, 2]]
        result = greedy_allocate(marginals, 5)
        self.assertEqual(result.amounts, (2, 2, 1))
        self.assertEqual(result.utility, utility_from_marginals(
            marginals, result.amounts))

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


if __name__ == "__main__":
    unittest.main()
