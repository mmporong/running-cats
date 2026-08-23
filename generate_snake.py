import heapq
import itertools
import os
from collections import defaultdict

import requests
from PIL import Image, ImageDraw


WIDTH = 52
HEIGHT = 7
MAX_SNAKE_LENGTH = 7
DIRECTIONS = ((0, 1), (0, -1), (1, 0), (-1, 0))

LEVEL_MAP = {
    "NONE": 0,
    "FIRST_QUARTILE": 1,
    "SECOND_QUARTILE": 2,
    "THIRD_QUARTILE": 3,
    "FOURTH_QUARTILE": 4,
}


def get_real_data():
    token = os.getenv("GH_TOKEN")
    username = os.getenv("GH_USERNAME", "mmporong")
    query = """
    query($username:String!) {
      user(login:$username) {
        contributionsCollection {
          contributionCalendar {
            weeks {
              contributionDays {
                contributionCount
                contributionLevel
              }
            }
          }
        }
      }
    }
    """
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.post(
            "https://api.github.com/graphql",
            json={"query": query, "variables": {"username": username}},
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        weeks = data["data"]["user"]["contributionsCollection"][
            "contributionCalendar"
        ]["weeks"][-WIDTH:]

        level_grid = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
        count_grid = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
        targets = []

        for week_index, week in enumerate(weeks):
            for day_index, day in enumerate(week["contributionDays"]):
                if day_index >= HEIGHT:
                    continue

                count = day["contributionCount"]
                level = LEVEL_MAP.get(day["contributionLevel"], 0)
                level_grid[day_index][week_index] = level
                count_grid[day_index][week_index] = count
                if count > 0:
                    targets.append((week_index, day_index))

        return level_grid, count_grid, targets
    except Exception as error:
        print(f"Error fetching data: {error}")
        fallback_targets = [(5, 2), (10, 5), (15, 1)]
        level_grid = [[0] * WIDTH for _ in range(HEIGHT)]
        count_grid = [[0] * WIDTH for _ in range(HEIGHT)]
        for x, y in fallback_targets:
            level_grid[y][x] = 1
            count_grid[y][x] = 1
        return level_grid, count_grid, fallback_targets


def _manhattan_to_nearest_goal(position, goals):
    x, y = position
    return min(abs(goal_x - x) + abs(goal_y - y) for goal_x, goal_y in goals)


def _advance_body(body, snake_length, next_position, eats_food):
    next_length = min(
        MAX_SNAKE_LENGTH,
        snake_length + (1 if eats_food else 0),
    )
    tail_will_move = len(body) + 1 > next_length
    occupied = body[:-1] if tail_will_move else body

    if next_position in occupied:
        return None

    next_body = (next_position,) + body
    if tail_will_move:
        next_body = next_body[:-1]
    return next_body, next_length


def _has_tail_escape(body, snake_length, remaining_targets, width, height):
    if len(body) < 2:
        return True
    escape_path = find_path_a_star(
        body,
        snake_length,
        {body[-1]},
        remaining_targets,
        width,
        height,
        require_tail_escape=False,
    )
    return escape_path is not None


def find_path_a_star(
    body,
    snake_length,
    goal_targets,
    remaining_targets,
    width=WIDTH,
    height=HEIGHT,
    require_tail_escape=True,
):
    """Find a collision-free path to the nearest goal in full snake-body state."""
    goals = frozenset(goal_targets)
    if not goals:
        return None

    start_body = tuple(body)
    if start_body[0] in goals:
        return []

    remaining = frozenset(remaining_targets)
    start_state = (start_body, snake_length, frozenset())
    frontier = []
    sequence = itertools.count()
    start_h = _manhattan_to_nearest_goal(start_body[0], goals)
    heapq.heappush(frontier, (start_h, 0, next(sequence), start_state))

    costs = {start_state: 0}
    came_from = {}

    while frontier:
        _, cost, _, state = heapq.heappop(frontier)
        if cost != costs.get(state):
            continue

        current_body, current_length, collected = state
        head_x, head_y = current_body[0]

        if current_body[0] in goals:
            path = []
            path_state = state
            while path_state != start_state:
                previous_state, position = came_from[path_state]
                path.append(position)
                path_state = previous_state
            path.reverse()

            targets_after_path = remaining.difference(path)
            if require_tail_escape and targets_after_path and not _has_tail_escape(
                current_body,
                current_length,
                targets_after_path,
                width,
                height,
            ):
                continue
            return path

        for dx, dy in DIRECTIONS:
            next_position = (head_x + dx, head_y + dy)
            next_x, next_y = next_position
            if not (0 <= next_x < width and 0 <= next_y < height):
                continue

            eats_food = next_position in remaining and next_position not in collected
            advanced = _advance_body(
                current_body,
                current_length,
                next_position,
                eats_food,
            )
            if advanced is None:
                continue

            next_body, next_length = advanced
            if next_length == MAX_SNAKE_LENGTH:
                next_collected = frozenset()
            else:
                next_collected = (
                    collected | {next_position} if eats_food else collected
                )
            next_state = (next_body, next_length, next_collected)
            next_cost = cost + 1
            if next_cost >= costs.get(next_state, float("inf")):
                continue

            costs[next_state] = next_cost
            came_from[next_state] = (state, next_position)
            heuristic = _manhattan_to_nearest_goal(next_position, goals)
            heapq.heappush(
                frontier,
                (next_cost + heuristic, next_cost, next(sequence), next_state),
            )

    return None


def find_priority_path(
    body,
    snake_length,
    remaining_targets,
    level_grid,
    count_grid,
    width=WIDTH,
    height=HEIGHT,
):
    """Prefer darker and higher-count cells, then the shortest safe A* route."""
    priority_groups = defaultdict(set)
    for x, y in remaining_targets:
        priority_groups[(level_grid[y][x], count_grid[y][x])].add((x, y))

    priorities = sorted(priority_groups, reverse=True)
    for require_tail_escape in (True, False):
        for priority in priorities:
            path = find_path_a_star(
                body,
                snake_length,
                priority_groups[priority],
                remaining_targets,
                width,
                height,
                require_tail_escape,
            )
            if path is not None:
                reached_target = path[-1] if path else body[0]
                return path, reached_target, priority

    return None, None, None


def simulate_snake(
    level_grid,
    count_grid,
    targets,
    width=WIDTH,
    height=HEIGHT,
):
    full_path = [(0, 0)]
    snake_lengths = [1]
    body_snapshots = [[(0, 0)]]
    selected_targets = []
    eaten_order = []

    body = ((0, 0),)
    snake_length = 1
    remaining_targets = set(targets)

    if body[0] in remaining_targets:
        remaining_targets.remove(body[0])
        eaten_order.append(body[0])
        snake_length = min(MAX_SNAKE_LENGTH, snake_length + 1)
        snake_lengths[0] = snake_length

    while remaining_targets:
        path, selected_target, _ = find_priority_path(
            body,
            snake_length,
            remaining_targets,
            level_grid,
            count_grid,
            width,
            height,
        )
        if path is None:
            raise RuntimeError(
                f"No collision-free route for {len(remaining_targets)} remaining targets"
            )

        selected_targets.append(selected_target)
        remaining_before = len(remaining_targets)

        for next_position in path:
            eats_food = next_position in remaining_targets
            advanced = _advance_body(
                body,
                snake_length,
                next_position,
                eats_food,
            )
            if advanced is None:
                raise RuntimeError(f"A* produced a self-collision at {next_position}")

            body, snake_length = advanced
            if eats_food:
                remaining_targets.remove(next_position)
                eaten_order.append(next_position)

            full_path.append(next_position)
            snake_lengths.append(snake_length)
            body_snapshots.append(list(body))

        if len(remaining_targets) >= remaining_before:
            raise RuntimeError("A* route did not consume a target")

    return {
        "full_path": full_path,
        "snake_lengths": snake_lengths,
        "body_snapshots": body_snapshots,
        "selected_targets": selected_targets,
        "eaten_order": eaten_order,
    }


def create_cat_snake(output_path="cat-snake.gif"):
    level_grid, count_grid, targets = get_real_data()
    cat_images = []
    for index in range(1, MAX_SNAKE_LENGTH + 1):
        name = f"{index:02}.png"
        if os.path.exists(name):
            cat_images.append(Image.open(name).convert("RGBA").resize((12, 12)))

    simulation = simulate_snake(level_grid, count_grid, targets)
    full_path = simulation["full_path"]
    body_snapshots = simulation["body_snapshots"]

    frames = []
    eaten_cells = set()
    target_cells = set(targets)
    colors = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]

    for frame_index, head_position in enumerate(full_path):
        image = Image.new("RGBA", (820, 160), (13, 17, 23, 255))
        draw = ImageDraw.Draw(image)

        if head_position in target_cells:
            eaten_cells.add(head_position)

        for column in range(WIDTH):
            for row in range(HEIGHT):
                x, y = column * 15 + 20, row * 15 + 20
                level = 0 if (column, row) in eaten_cells else level_grid[row][column]
                draw.rounded_rectangle(
                    [x, y, x + 12, y + 12],
                    radius=2,
                    fill=colors[level],
                )

        for image_index, (column, row) in enumerate(body_snapshots[frame_index]):
            if image_index < len(cat_images):
                image.paste(
                    cat_images[image_index],
                    (column * 15 + 20, row * 15 + 20),
                    cat_images[image_index],
                )

        frames.append(image)

    if frames:
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=100,
            loop=0,
            disposal=2,
        )


if __name__ == "__main__":
    create_cat_snake()
