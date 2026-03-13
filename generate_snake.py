import os
import requests
import base64
from PIL import Image, ImageDraw

# 1. 설정
GITHUB_USERNAME = "mmporong"
CAT_COUNT = 20
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 200
GRID_SIZE = 12
SPACING = 3

def get_contribution_data():
    # 실제 깃허브 잔디 데이터를 가져오려면 토큰이 필요하지만, 
    # 일단은 형태를 잡기 위해 임의의 잔디 데이터를 생성하는 로직으로 구성합니다.
    # (추후 깃허브 API 연동 가능)
    rows, cols = 7, 52
    return [[(i + j) % 5 for j in range(cols)] for i in range(rows)]

def create_cat_snake_gif():
    # 이미지 로드 (01.png ~ 20.png)
    cat_imgs = []
    for i in range(1, CAT_COUNT + 1):
        name = f"{str(i).zfill(2)}.png"
        if os.path.exists(name):
            cat_imgs.append(Image.open(name).convert("RGBA").resize((GRID_SIZE+4, GRID_SIZE+4)))

    if not cat_imgs: return

    data = get_contribution_data()
    frames = []
    
    # 애니메이션 경로 (뱀 게임처럼 ㄷ자로 이동)
    path = []
    for col in range(52):
        row_range = range(7) if col % 2 == 0 else range(6, -1, -1)
        for row in row_range:
            path.append((col, row))

    # 100프레임 동안 이동
    for f in range(len(path) + CAT_COUNT):
        img = Image.new("RGBA", (CANVAS_WIDTH, CANVAS_HEIGHT), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # 1. 잔디 그리기
        for col in range(52):
            for row in range(7):
                x = col * (GRID_SIZE + SPACING) + 30
                y = row * (GRID_SIZE + SPACING) + 30
                # 잔디 색상 (기존 뱀 게임과 동일한 색상셋)
                colors = ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"]
                color = colors[data[row][col]]
                
                # 고양이가 이미 지나간 자리는 먹힌 것처럼 연하게 표시 (먹는 연출)
                path_idx = next((i for i, p in enumerate(path) if p == (col, row)), -1)
                if path_idx != -1 and path_idx < f - CAT_COUNT:
                    color = "#eeeeee" # 먹힌 잔디 색
                
                draw.rectangle([x, y, x + GRID_SIZE, y + GRID_SIZE], fill=color)

        # 2. 고양이 기차 그리기 (뱀 마디)
        for i in range(CAT_COUNT):
            idx = f - i
            if 0 <= idx < len(path):
                col, row = path[idx]
                x = col * (GRID_SIZE + SPACING) + 30 - 2
                y = row * (GRID_SIZE + SPACING) + 30 - 2
                img.paste(cat_imgs[i], (x, y), cat_imgs[i])

        frames.append(img)

    # 3. GIF 저장
    frames[0].save("cat-snake.gif", save_all=True, append_images=frames[1:], duration=100, loop=0, disposal=2)

if __name__ == "__main__":
    create_cat_snake_gif()
