import os
import requests
from PIL import Image, ImageDraw
from collections import deque

def get_real_data():
    token = os.getenv("GH_TOKEN")
    username = "mmporong"
    query = """
    query($username:String!) {
      user(login:$username) {
        contributionsCollection {
          contributionCalendar {
            weeks { contributionDays { contributionCount } }
          }
        }
      }
    }
    """
    headers = {"Authorization": f"Bearer {token}"}
    try:
        res = requests.post("https://api.github.com/graphql", json={'query': query, 'variables': {'username': username}}, headers=headers)
        weeks = res.json()['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
        grid = [[0 for _ in range(52)] for _ in range(7)]
        targets = []
        for w_idx, w in enumerate(weeks):
            for d_idx, d in enumerate(w['contributionDays']):
                if w_idx < 52 and d_idx < 7:
                    count = d['contributionCount']
                    grid[d_idx][w_idx] = count
                    if count > 0: targets.append((w_idx, d_idx))
        return grid, targets
    except:
        return [[0]*52 for _ in range(7)], [(5,2), (10,5), (15,1)]

# 🌟 최단 경로 탐색 및 몸통 충돌 회피 알고리즘
def find_path(start, target, body, width=52, height=7):
    queue = deque([(start, [])])
    visited = {start}
    visited.update(set(body)) # 현재 몸통 위치는 장애물로 간주

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
    # 01.png(머리) ~ 05.png(꼬리) 로드
    for i in range(1, 6):
        name = f"{str(i).zfill(2)}.png"
        if os.path.exists(name):
            cat_imgs.append(Image.open(name).convert("RGBA").resize((12, 12)))

    # 1. 게임 시뮬레이션 시작
    full_path = [(0, 0)]
    snake_lengths = [1] # 프레임별 뱀의 길이 저장
    body_snapshots = [[(0, 0)]] # 프레임별 몸통 좌표 저장
    
    curr_pos = (0, 0)
    curr_body = [(0, 0)]
    curr_len = 1
    remaining_targets = targets[:]

    while remaining_targets:
        # 가장 가까운 타겟 선정
        remaining_targets.sort(key=lambda t: abs(t[0]-curr_pos[0]) + abs(t[1]-curr_pos[1]))
        target = remaining_targets.pop(0)
        
        # 타겟까지의 경로 탐색 (몸통 회피 포함)
        sub_path = find_path(curr_pos, target, curr_body)
        if not sub_path: continue # 경로가 없으면 다음 타겟으로

        for next_step in sub_path:
            curr_pos = next_step
            curr_body.insert(0, curr_pos)
            
            # 먹이 섭취 시 성장 (최대 5)
            if curr_pos == target:
                curr_len = min(5, curr_len + 1)
            
            if len(curr_body) > curr_len:
                curr_body.pop()
            
            full_path.append(curr_pos)
            snake_lengths.append(curr_len)
            body_snapshots.append(list(curr_body))

    # 2. 렌더링
    frames = []
    eaten_cells = set()
    for f in range(len(full_path)):
        img = Image.new("RGBA", (820, 160), (13, 17, 23, 255))
        draw = ImageDraw.Draw(img)
        
        # 현재 프레임의 머리가 먹이를 먹었는지 체크
        if grid_data[full_path[f][1]][full_path[f][0]] > 0:
            eaten_cells.add(full_path[f])

        # 그리드 그리기
        for col in range(52):
            for row in range(7):
                x, y = col * 15 + 20, row * 15 + 20
                colors = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
                color = colors[0 if (col, row) in eaten_cells else (0 if grid_data[row][col] == 0 else 1)]
                draw.rounded_rectangle([x, y, x + 12, y + 12], radius=2, fill=color)

        # 뱀(고양이) 그리기
        for i, (c, r) in enumerate(body_snapshots[f]):
            img.paste(cat_imgs[i], (c * 15 + 20, r * 15 + 20), cat_imgs[i])

        frames.append(img)

    frames[0].save("cat-snake.gif", save_all=True, append_images=frames[1:], duration=100, loop=0, disposal=2)

if __name__ == "__main__":
    create_cat_snake()
