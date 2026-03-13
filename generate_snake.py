import os
import requests
import base64
from PIL import Image, ImageDraw

# 1. 설정 및 데이터 수집
def get_contributions():
    token = os.getenv("GH_TOKEN")
    username = "mmporong"
    query = """
    query($username:String!) {
      user(login:$username) {
        contributionsCollection {
          contributionCalendar {
            weeks { contributionDays { contributionCount color } }
          }
        }
      }
    }
    """
    headers = {"Authorization": f"Bearer {token}"}
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

def create_cat_snake():
    data = get_contributions()
    cat_imgs = []
    for i in range(1, 21):
        name = f"{str(i).zfill(2)}.png"
        if os.path.exists(name):
            cat_imgs.append(Image.open(name).convert("RGBA").resize((16, 16)))

    # 2. 뱀 게임 경로 생성 (S자 이동)
    path = []
    for col in range(52):
        rows = range(7) if col % 2 == 0 else range(6, -1, -1)
        for row in rows: path.append((col, row))

    frames = []
    # 4칸씩 건너뛰며 프레임 생성 (속도 조절)
    for f in range(0, len(path) + 20, 3):
        img = Image.new("RGBA", (820, 150), (13, 17, 23, 255)) # 깃허브 다크모드 배경색
        draw = ImageDraw.Draw(img)
        
        # 3. 잔디밭 그리기
        for col in range(52):
            for row in range(7):
                x, y = col * 15 + 20, row * 15 + 20
                colors = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
                color = colors[data[row][col]]
                
                # 고양이가 지나간 자리는 '먹힌' 효과 (배경색으로)
                for i in range(max(0, f-20), f):
                    if i < len(path) and path[i] == (col, row):
                        color = "#161b22" # 먹힌 자리
                
                draw.rounded_rectangle([x, y, x + 12, y + 12], radius=2, fill=color)

        # 4. 고양이 기차(뱀 마디) 배치
        for i in range(len(cat_imgs)):
            idx = f - i
            if 0 <= idx < len(path):
                c, r = path[idx]
                img.paste(cat_imgs[i], (c * 15 + 18, r * 15 + 18), cat_imgs[i])
        
        frames.append(img)

    frames[0].save("cat-snake.gif", save_all=True, append_images=frames[1:], duration=60, loop=0, disposal=2)

if __name__ == "__main__":
    create_cat_snake()
