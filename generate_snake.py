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
        for w_idx, w in enumerate(weeks):
            for d_idx, d in enumerate(w['contributionDays']):
                if w_idx < 52 and d_idx < 7:
                    count = d['contributionCount']
                    # snk 스타일의 5단계 레벨링
                    level = 0 if count == 0 else (1 if count < 3 else (2 if count < 6 else (3 if count < 10 else 4)))
                    grid[d_idx][w_idx] = level
        return grid
    except:
        return [[(i + j) % 5 for j in range(52)] for i in range(7)]

def create_cat_snake():
    data = get_real_data()
    cat_imgs = []
    # 01.png ~ 20.png 로드
    for i in range(1, 21):
        name = f"{str(i).zfill(2)}.png"
        if os.path.exists(name):
            cat_imgs.append(Image.open(name).convert("RGBA").resize((12, 12)))

    # 🌟 1. 수평 S-Curve 경로 생성 (snk 이동 방식)
    # Row 0: L->R, Row 1: R->L, Row 2: L->R ...
    path = []
    for r in range(7):
        cols = range(52) if r % 2 == 0 else range(51, -1, -1)
        for c in cols:
            path.append((c, r))

    frames = []
    eaten_cells = set()
    snake_max_len = len(cat_imgs) # 고양이 이미지 개수만큼 꼬리 길이 설정
    
    # 🌟 2. 시뮬레이션: 전체 경로 순회
    for f in range(len(path) + snake_max_len):
        # 깃허브 다크모드 배경색 (#0d1117 근사치)
        img = Image.new("RGBA", (820, 150), (13, 17, 23, 255))
        draw = ImageDraw.Draw(img)
        
        if f < len(path):
            head_pos = path[f]
            if data[head_pos[1]][head_pos[0]] > 0:
                eaten_cells.add(head_pos)

        # 3. 보드 렌더링 (그리드 정렬)
        for col in range(52):
            for row in range(7):
                x, y = col * 15 + 20, row * 15 + 20
                colors = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
                color = colors[data[row][col]]
                
                if (col, row) in eaten_cells:
                    color = "#161b22"
                
                # snk 특유의 둥근 사각형
                draw.rounded_rectangle([x, y, x + 12, y + 12], radius=2, fill=color)

        # 4. 고양이 몸통 렌더링 (Trailing Logic)
        active_segments = 0
        for i in range(snake_max_len):
            idx = f - i
            if 0 <= idx < len(path):
                c, r = path[idx]
                x, y = c * 15 + 20, r * 15 + 20
                # 인덱스에 맞는 고양이 이미지 배치
                img.paste(cat_imgs[i], (x, y), cat_imgs[i])
                active_segments += 1
        
        if active_segments > 0:
            frames.append(img)

    # 🌟 5. GIF 저장 (속도 100ms로 조절)
    frames[0].save(
        "cat-snake.gif",
        save_all=True,
        append_images=frames[1:],
        duration=100, 
        loop=0,
        disposal=2
    )

if __name__ == "__main__":
    create_cat_snake()
