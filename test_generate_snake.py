import unittest

from generate_snake import (
    HEIGHT,
    MAX_SNAKE_LENGTH,
    WIDTH,
    find_path_a_star,
    find_priority_path,
    simulate_snake,
)


def make_grids(values):
    level_grid = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
    count_grid = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
    for position, (level, count) in values.items():
        x, y = position
        level_grid[y][x] = level
        count_grid[y][x] = count
    return level_grid, count_grid


class CatSnakePathfindingTests(unittest.TestCase):
    def assert_valid_simulation(self, simulation, targets):
        self.assertEqual(set(simulation["eaten_order"]), set(targets))
        self.assertEqual(len(simulation["full_path"]), len(simulation["body_snapshots"]))

        previous = simulation["full_path"][0]
        for position, body in zip(
            simulation["full_path"][1:],
            simulation["body_snapshots"][1:],
        ):
            self.assertEqual(
                abs(position[0] - previous[0]) + abs(position[1] - previous[1]),
                1,
            )
            self.assertEqual(len(body), len(set(body)))
            self.assertLessEqual(len(body), MAX_SNAKE_LENGTH)
            previous = position

    def test_astar_uses_cells_as_the_tail_vacates_them(self):
        body = ((1, 0), (2, 0), (2, 1), (2, 2), (1, 2), (0, 2))
        target = (3, 0)

        path = find_path_a_star(body, 6, {target}, {target})

        self.assertIsNotNone(path)
        self.assertEqual(path[-1], target)
        self.assertEqual(
            path,
            [(1, 1), (1, 2), (2, 2), (2, 1), (2, 0), (3, 0)],
        )

    def test_previous_static_body_counterexample_is_fully_consumed(self):
        targets = {(0, 1), (0, 2), (1, 0), (1, 2), (2, 2), (3, 0)}
        values = {target: (1, 1) for target in targets}
        level_grid, count_grid = make_grids(values)

        simulation = simulate_snake(level_grid, count_grid, targets)

        self.assert_valid_simulation(simulation, targets)

    def test_darker_and_higher_count_target_is_selected_first(self):
        low = (0, 2)
        darker_low_count = (3, 0)
        darker_high_count = (4, 1)
        targets = {low, darker_low_count, darker_high_count}
        level_grid, count_grid = make_grids(
            {
                low: (1, 100),
                darker_low_count: (4, 2),
                darker_high_count: (4, 20),
            }
        )

        path, target, priority = find_priority_path(
            ((0, 0),),
            1,
            targets,
            level_grid,
            count_grid,
        )

        self.assertIsNotNone(path)
        self.assertEqual(target, darker_high_count)
        self.assertEqual(priority, (4, 20))

    def test_shortest_path_breaks_equal_priority_ties(self):
        near = (1, 0)
        far = (5, 0)
        targets = {near, far}
        level_grid, count_grid = make_grids(
            {
                near: (4, 10),
                far: (4, 10),
            }
        )

        path, target, priority = find_priority_path(
            ((0, 0),),
            1,
            targets,
            level_grid,
            count_grid,
        )

        self.assertEqual(path, [near])
        self.assertEqual(target, near)
        self.assertEqual(priority, (4, 10))

    def test_food_under_starting_head_is_consumed_without_overlap(self):
        targets = {(0, 0), (2, 0)}
        level_grid, count_grid = make_grids(
            {
                (0, 0): (4, 10),
                (2, 0): (1, 1),
            }
        )

        simulation = simulate_snake(level_grid, count_grid, targets)

        self.assertEqual(simulation["eaten_order"][0], (0, 0))
        self.assert_valid_simulation(simulation, targets)

    def test_dense_priority_board_does_not_choose_a_trapping_route(self):
        values = {
            (0, 1): (2, 4),
            (0, 2): (4, 23),
            (0, 3): (3, 83),
            (1, 0): (3, 4),
            (1, 1): (3, 13),
            (1, 2): (4, 87),
            (1, 3): (1, 55),
            (2, 0): (3, 81),
            (2, 1): (2, 17),
            (2, 2): (2, 52),
            (3, 0): (2, 46),
            (3, 1): (3, 44),
            (3, 2): (3, 13),
            (4, 0): (1, 17),
            (4, 1): (3, 74),
            (4, 3): (1, 90),
            (5, 1): (1, 74),
            (5, 3): (2, 35),
        }
        level_grid, count_grid = make_grids(values)

        simulation = simulate_snake(
            level_grid,
            count_grid,
            set(values),
            width=6,
            height=4,
        )

        self.assert_valid_simulation(simulation, values)

    def test_full_food_board_falls_back_when_tail_check_is_too_strict(self):
        values = {
            (0, 0): (4, 70),
            (0, 1): (4, 91),
            (0, 2): (4, 10),
            (0, 3): (2, 72),
            (1, 0): (4, 13),
            (1, 1): (2, 34),
            (1, 2): (3, 88),
            (1, 3): (2, 68),
            (2, 0): (4, 67),
            (2, 1): (3, 24),
            (2, 2): (3, 98),
            (2, 3): (1, 9),
            (3, 0): (2, 45),
            (3, 1): (2, 55),
            (3, 2): (3, 90),
            (3, 3): (2, 46),
            (4, 0): (2, 35),
            (4, 1): (1, 80),
            (4, 2): (1, 49),
            (4, 3): (1, 39),
            (5, 0): (1, 50),
            (5, 1): (3, 3),
            (5, 2): (1, 76),
            (5, 3): (1, 33),
        }
        level_grid, count_grid = make_grids(values)

        simulation = simulate_snake(
            level_grid,
            count_grid,
            set(values),
            width=6,
            height=4,
        )

        self.assert_valid_simulation(simulation, values)


if __name__ == "__main__":
    unittest.main()
