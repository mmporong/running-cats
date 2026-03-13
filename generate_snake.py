import os
import requests
import base64
from PIL import Image, ImageDraw

def get_contributions(token, username):
    query = """
    query($username:String!) {
      user(login:$username) {
        contributionsCollection {
          contributionCalendar {
            weeks {
              contributionDays {
                contributionCount
                color
              }
            }
          }
        }
      }
    }
    """
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post("https://api.github.com/graphql", json={'query': query, 'variables': {'username': username}}, headers=headers)
    
    weeks = response.json()['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
    # 7행 52열 데이터로 변환
    grid = []
    for r in range(7):
        row = []
        for w in weeks:
            if r < len(w['contributionDays']):
                count = w['contributionDays'][r]['contributionCount']
                # 커밋 수에 따른 색상 단계 (0~4)
                level = 0 if count == 0 else (1 if count < 3 else (2 if count < 6 else (3 if count < 10 else 4)))
                row.append(level)
            else:
                row.append(0)
        grid.append(row)
    return grid

def create_cat_snake_gif():
    token = os.getenv("GH_TOKEN")
    data = get_contributions(token, "mmporong")
    
    cat_imgs = []
    for i in range(1, 21):
        name = f"{str(i).zfill(2)}.png"
        if os.path.exists(name):
            cat_imgs.append(Image.open(name).convert("RGBA").resize((14, 14)))

    path = []
    for col in range(52):
        row_range = range(7) if col % 2 == 0 else range(6, -1, -1)
        for row in row_range: path.append((col, row))

    frames = []
    for f in range(0, len(path) + 20, 2): # 2칸씩 이동해 속도감 조절
        img = Image.new("RGBA", (800, 200), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # 잔디 그리기
        for col in range(52):
            for row in range(7):
                x, y = col * 15 + 10, row * 15 + 10
                colors = ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"]
                color = colors[data[row][col]]
                
                # 고양이 기차가 지나간 곳은 '먹힌' 효과 (배경색으로)
                for idx in range(max(0, f-20), f):
                    if idx < len(path) and path[idx] == (col, row):
                        color = "#ffffff" 
                
                draw.rectangle([x, y, x + 12, y + 12], fill=color)

        # 고양이 배치
        for i in range(20):
            idx = f - i
            if 0 <= idx < len(path):
                c, r = path[idx]
                img.paste(cat_imgs[i], (c * 15 + 8, r * 15 + 8), cat_imgs[i])
        
        frames.append(img)

    frames[0].save("cat-snake.gif", save_all=True, append_images=frames[1:], duration=80, loop=0, disposal=2)

if __name__ == "__main__":
    create_cat_snake_gif()
