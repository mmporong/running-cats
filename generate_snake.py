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
        grid = []
        for r in range(7):
            row = []
            for w in weeks:
                if r < len(w['contributionDays']):
                    count = w['contributionDays'][r]['contributionCount']
                    level = 0 if count == 0 else (1 if count < 3 else (2 if count < 6 else (3 if count < 10 else 4)))
                    row.append(level)
                else: row.append(0)
            grid.append(row)
        return grid
    except:
        return [[(i + j) % 5 for j in range(52)] for i in range(7)]

def create_cat_snake():
    data = get_real_data()
    cat_imgs = []
    for i in range(1, 21):
        name = f"{str(i).zfill(2)}.png"
        if os.path.exists(name):
            cat_imgs.append(Image.open(name).convert("RGBA").resize((12, 12)))

    # S자 이동 경로 (뱀 이동 로직)
    path = []
    for col in range(52):
        rows = range(7) if col % 2 == 0 else range(6, -1, -1)
        for row in rows: path.append((col, row))

    frames = []
    snake_len = 1
    eaten = set()
    
    # 애니메이션 시뮬레이션 (f = 현재 머리의 위치 index)
    for f in range(len(path)):
        img = Image.new("RGBA", (820, 160), (13, 17, 23, 255))
        draw = ImageDraw.Draw(img)
        
        # 1. 성장 체크: 머리가 초록 잔디를 밟으면 길어짐
        head_pos = path[f]
        if data[head_pos[1]][head_pos[0]] > 0 and head_pos not in eaten:
            snake_len = min(20, snake_len + 1)
            eaten.add(head_pos)

        # 2. 잔디 그리기
        for col in range(52):
            for row in range(7):
                x, y = col * 15 + 20, row * 15 + 20
                colors = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
                color = colors[data[row][col]]
                if (col, row) in eaten: color = "#161b22" # 먹힌 자리
                draw.rectangle([x, y, x + 12, y + 12], fill=color)

        # 3. 고양이 몸체 그리기 (머리부터 꼬리까지 순차 배치)
        for i in range(snake_len):
            idx = f - i
            if idx >= 0:
                c, r = path[idx]
                # 고양이 이미지를 순서대로 할당 (01번이 머리, 뒤로 갈수록 다음 번호)
                cat_idx = i % len(cat_imgs)
                img.paste(cat_imgs[cat_idx], (c * 15 + 20, r * 15 + 20), cat_imgs[cat_idx])

        # 모든 프레임을 다 넣으면 용량이 너무 커지므로 2프레임당 1개씩 추출
        if f % 2 == 0:
            frames.append(img)

    frames[0].save("cat-snake.gif", save_all=True, append_images=frames[1:], duration=60, loop=0, disposal=2)

if __name__ == "__main__":
    create_cat_snake()
