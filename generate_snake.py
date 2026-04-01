import os
import requests
from PIL import Image, ImageDraw
from collections import deque

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
    
    level_map = {
        "NONE": 0,
        "FIRST_QUARTILE": 1,
        "SECOND_QUARTILE": 2,
        "THIRD_QUARTILE": 3,
        "FOURTH_QUARTILE": 4
    }
    
    try:
        res = requests.post("https://api.github.com/graphql", json={'query': query, 'variables': {'username': username}}, headers=headers)
        data = res.json()
        weeks = data['data']['user']['contributionsCollection']['contributionCalendar']['weeks'][-52:]
        grid = [[0 for _ in range(52)] for _ in range(7)]
        targets = []
        for w_idx, w in enumerate(weeks):
            for d_idx, d in enumerate(w['contributionDays']):
                if d_idx < 7:
                    count = d['contributionCount']
                    level_str = d['contributionLevel']
                    level = level_map.get(level_str, 0)
                    grid[d_idx][w_idx] = level
                    if count > 0: targets.append((w_idx, d_idx))
        return grid, targets
    except Exception as e:
        print(f"Error fetching data: {e}")
        # 기본값 (실패 시 예시 타겟)
        return [[0]*52 for _ in range(7)], [(5,2), (10,5), (15,1)]

# 🌟 최단 경로 탐색 및 몸통 충돌 회피 알고리즘
def find_path(start, target, body, width=52, height=7):
    if start == target:
        return [target]

    # 꼬리 쪽은 이동하면서 빠지므로, 머리 쪽 절반만 장애물로 취급
    safe_body = set(body[:max(1, len(body) // 2)])

    queue = deque([(start, [])])
    visited = {start}
    visited.update(safe_body)

    while queue:
        (x, y), path = queue.popleft()
        if (x, y) == target: return path

        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append(((nx, ny), path + [(nx, ny)]))

    # 몸통 회피로 경로를 못 찾으면, 몸통 무시하고 재탐색
    queue = deque([(start, [])])
    visited = {start}
    while queue:
        (x, y), path = queue.popleft()
        if (x, y) == target: return path
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append(((nx, ny), path + [(nx, ny)]))
    return None

def create_cat_snake():
    grid_data, targets = get_real_data()
    cat_imgs = []
    # 01.png(머리) ~ 07.png(꼬리) 로드
    for i in range(1, 8):
        name = f"{str(i).zfill(2)}.png"
        if os.path.exists(name):
            cat_imgs.append(Image.open(name).convert("RGBA").resize((12, 12)))

    # 1. 게임 시뮬레이션 시작
    full_path = [(0, 0)]
    snake_lengths = [1]
    body_snapshots = [[(0, 0)]]
    
    curr_pos = (0, 0)
    curr_body = [(0, 0)]
    curr_len = 1
    remaining_targets = targets[:]

    max_retries = len(remaining_targets) * 2
    retry_count = 0

    while remaining_targets and retry_count < max_retries:
        # 가장 가까운 타겟 선정
        remaining_targets.sort(key=lambda t: abs(t[0]-curr_pos[0]) + abs(t[1]-curr_pos[1]))
        target = remaining_targets.pop(0)

        # 타겟까지의 경로 탐색 (몸통 회피 포함)
        sub_path = find_path(curr_pos, target, curr_body)
        if not sub_path:
            # 경로 실패 시 타겟을 리스트 끝에 재삽입 (영구 손실 방지)
            remaining_targets.append(target)
            retry_count += 1
            continue

        retry_count = 0

        for next_step in sub_path:
            curr_pos = next_step
            curr_body.insert(0, curr_pos)

            # 먹이 섭취 시 성장 (최대 7)
            if curr_pos == target or curr_pos in remaining_targets:
                curr_len = min(7, curr_len + 1)
                # 경로 중간에 다른 타겟을 지나가면 먹기 처리
                if curr_pos in remaining_targets:
                    remaining_targets.remove(curr_pos)

            if len(curr_body) > curr_len:
                curr_body.pop()

            full_path.append(curr_pos)
            snake_lengths.append(curr_len)
            body_snapshots.append(list(curr_body))

    # 진단 출력
    total_targets = len(targets)
    eaten_count = total_targets - len(remaining_targets)
    print(f"[진단] 전체 타겟: {total_targets}, 먹은 수: {eaten_count}, 남은 수: {len(remaining_targets)}, 총 프레임: {len(full_path)}")
    if remaining_targets:
        print(f"[진단] 못 먹은 타겟: {remaining_targets[:20]}")

    # 2. 렌더링
    frames = []
    eaten_cells = set()
    for f in range(len(full_path)):
        img = Image.new("RGBA", (820, 160), (13, 17, 23, 255))
        draw = ImageDraw.Draw(img)
        
        # 현재 프레임의 머리가 먹이를 먹었는지 체크
        # grid_data에는 이제 레벨이 저장되어 있으므로, 0보다 크면 먹이로 간주
        if grid_data[full_path[f][1]][full_path[f][0]] > 0:
            eaten_cells.add(full_path[f])

        # 그리드 그리기
        for col in range(52):
            for row in range(7):
                x, y = col * 15 + 20, row * 15 + 20
                colors = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
                if (col, row) in eaten_cells:
                    level = 0
                else:
                    level = grid_data[row][col]
                draw.rounded_rectangle([x, y, x + 12, y + 12], radius=2, fill=colors[level])

        # 뱀(고양이) 그리기
        for i, (c, r) in enumerate(body_snapshots[f]):
            if i < len(cat_imgs):
                img.paste(cat_imgs[i], (c * 15 + 20, r * 15 + 20), cat_imgs[i])

        frames.append(img)

    if frames:
        frames[0].save("cat-snake.gif", save_all=True, append_images=frames[1:], duration=100, loop=0, disposal=2)

if __name__ == "__main__":
    create_cat_snake()
