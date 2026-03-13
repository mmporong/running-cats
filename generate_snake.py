import os
import requests
from PIL import Image, ImageDraw

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
                    if count > 0:
                        targets.append((w_idx, d_idx)) # 초록 잔디를 목표물로 등록
        return grid, targets
    except:
        return [[0]*52 for _ in range(7)], [(10,2), (20,5), (30,1)]

def create_cat_snake():
    grid_data, targets = get_real_data()
    cat_imgs = []
    # snk와 동일하게 머리 포함 5마디만 사용 (01~05.png)
    for i in range(1, 6):
        name = f"{str(i).zfill(2)}.png"
        if os.path.exists(name):
            cat_imgs.append(Image.open(name).convert("RGBA").resize((12, 12)))

    # 1. 뱀 게임 이동 경로 생성 (Greedy Target Hunting)
    path = [(0, 0)]
    curr_x, curr_y = 0, 0
    remaining_targets = targets[:]

    while remaining_targets:
        # 가장 가까운 목표물 찾기 (Manhattan Distance)
        remaining_targets.sort(key=lambda t: abs(t[0]-curr_x) + abs(t[1]-curr_y))
        target = remaining_targets.pop(0)
        
        # 목표물까지 한 칸씩 이동 (X축 이동 후 Y축 이동)
        while curr_x != target[0]:
            curr_x += 1 if target[0] > curr_x else -1
            path.append((curr_x, curr_y))
        while curr_y != target[1]:
            curr_y += 1 if target[1] > curr_y else -1
            path.append((curr_x, curr_y))

    # 2. 프레임 생성
    frames = []
    eaten_cells = set()
    snake_len = 5 # snk 표준 길이
    
    for f in range(len(path) + snake_len):
        img = Image.new("RGBA", (820, 150), (13, 17, 23, 255))
        draw = ImageDraw.Draw(img)
        
        # 머리가 목표물에 도달하면 먹기 처리
        if f < len(path):
            head_pos = path[f]
            if grid_data[head_pos[1]][head_pos[0]] > 0:
                eaten_cells.add(head_pos)

        # 3. 보드 그리기 (12px 셀, 3px 간격)
        for col in range(52):
            for row in range(7):
                x, y = col * 15 + 20, row * 15 + 20
                count = grid_data[row][col]
                colors = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
                level = 0 if count == 0 else (1 if count < 3 else (2 if count < 6 else (3 if count < 10 else 4)))
                color = colors[level]
                
                if (col, row) in eaten_cells:
                    color = "#161b22" # 먹힌 잔디 지우기
                
                draw.rounded_rectangle([x, y, x + 12, y + 12], radius=2, fill=color)

        # 4. 고양이 몸통(5마디) 그리기
        active = False
        for i in range(snake_len):
            idx = f - i
            if 0 <= idx < len(path):
                c, r = path[idx]
                # 01.png는 머리, 02~05.png는 몸통
                img.paste(cat_imgs[i], (c * 15 + 20, r * 15 + 20), cat_imgs[i])
                active = True
        
        if active:
            frames.append(img)

    # 3. GIF 저장 (snk와 유사한 속도 100ms)
    frames[0].save("cat-snake.gif", save_all=True, append_images=frames[1:], duration=100, loop=0, disposal=2)

if __name__ == "__main__":
    create_cat_snake()
