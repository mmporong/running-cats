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
        # 에러 발생 시 테스트용 가짜 데이터
        return [[(i + j) % 5 for j in range(52)] for i in range(7)]

def create_cat_snake():
    data = get_real_data()
    cat_imgs = []
    # 01.png ~ 20.png 로드
    for i in range(1, 21):
        name = f"{str(i).zfill(2)}.png"
        if os.path.exists(name):
            cat_imgs.append(Image.open(name).convert("RGBA").resize((12, 12)))

    # 1. S자 이동 경로 계산 (Snake Path)
    path = []
    for col in range(52):
        rows = range(7) if col % 2 == 0 else range(6, -1, -1)
        for row in rows:
            path.append((col, row))

    frames = []
    snake_len = 1
    eaten_cells = set()
    
    # 2. 프레임별 시뮬레이션
    for f in range(len(path)):
        # 배경 (깃허브 다크모드 색상)
        img = Image.new("RGBA", (820, 160), (13, 17, 23, 255))
        draw = ImageDraw.Draw(img)
        
        # 현재 머리 위치
        head_pos = path[f]
        
        # 성장 로직: 머리가 잔디(커밋 > 0)를 밟으면 몸길이 증가
        if data[head_pos[1]][head_pos[0]] > 0 and head_pos not in eaten_cells:
            snake_len = min(20, snake_len + 1)
            eaten_cells.add(head_pos)

        # 3. 잔디밭 렌더링
        for col in range(52):
            for row in range(7):
                x, y = col * 15 + 20, row * 15 + 20
                colors = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
                color = colors[data[row][col]]
                
                # 이미 먹힌 잔디는 배경색으로 지움
                if (col, row) in eaten_cells:
                    color = "#161b22"
                
                draw.rounded_rectangle([x, y, x + 12, y + 12], radius=2, fill=color)

        # 4. 고양이 기차(Snake Body) 렌더링
        # 머리(f)부터 꼬리(f - snake_len)까지 순서대로 그림
        for i in range(snake_len):
            idx = f - i
            if idx >= 0:
                c, r = path[idx]
                # 고양이 이미지를 순환하며 할당
                img.paste(cat_imgs[i % len(cat_imgs)], (c * 15 + 20, r * 15 + 20), cat_imgs[i % len(cat_imgs)])

        # 모든 프레임을 다 넣으면 용량이 크므로 2프레임당 1개씩 추출
        if f % 2 == 0:
            frames.append(img)

    # 5. GIF 저장
    frames[0].save(
        "cat-snake.gif",
        save_all=True,
        append_images=frames[1:],
        duration=60,
        loop=0,
        disposal=2
    )

if __name__ == "__main__":
    create_cat_snake()
