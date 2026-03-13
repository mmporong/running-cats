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
                    # snk와 동일한 5단계 레벨링
                    level = 0 if count == 0 else (1 if count < 3 else (2 if count < 6 else (3 if count < 10 else 4)))
                    grid[d_idx][w_idx] = level
        return grid
    except:
        return [[(i + j) % 5 for j in range(52)] for i in range(7)]

def create_cat_snake():
    data = get_real_data()
    cat_imgs = []
    # 01.png ~ 20.png 로드 (사용자 리포지토리에 있는 고양이 이미지 사용)
    for i in range(1, 21):
        name = f"{str(i).zfill(2)}.png"
        if os.path.exists(name):
            cat_imgs.append(Image.open(name).convert("RGBA").resize((12, 12)))

    # 1. 수평 S-Curve 경로 생성 (snk의 정석 이동 방식)
    # Row 0: L->R, Row 1: R->L, Row 2: L->R ...
    path = []
    for r in range(7):
        cols = range(52) if r % 2 == 0 else range(51, -1, -1)
        for c in cols:
            path.append((c, r))

    frames = []
    eaten_cells = set()
    # snk 스타일의 몸통 길이 (일반적으로 5~9마디가 가장 적당함)
    snake_max_len = len(cat_imgs) # 보유한 고양이 이미지 수만큼 최대 길이 설정
    
    # 2. 시뮬레이션: 전체 경로 + 꼬리가 빠져나가는 여유 프레임
    for f in range(len(path) + snake_max_len):
        img = Image.new("RGBA", (820, 160), (13, 17, 23, 255)) # GitHub Dark Mode 배경색
        draw = ImageDraw.Draw(img)
        
        # 머리 위치 확인 및 먹기 판정
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
                
                # 먹힌 잔디는 배경색으로 처리
                if (col, row) in eaten_cells:
                    color = "#161b22"
                
                # 둥근 사각형으로 snk 느낌 극대화
                draw.rounded_rectangle([x, y, x + 12, y + 12], radius=2, fill=color)

        # 4. 고양이 몸통 렌더링 (Trailing Logic)
        # f부터 f-snake_len까지의 좌표를 역순으로 추적하여 고양이 배치
        active_segments = 0
        for i in range(snake_max_len):
            idx = f - i
            if 0 <= idx < len(path):
                c, r = path[idx]
                x, y = c * 15 + 20, r * 15 + 20
                # 01.png가 머리, 나머지가 몸통
                img.paste(cat_imgs[i % len(cat_imgs)], (x, y), cat_imgs[i % len(cat_imgs)])
                active_segments += 1
        
        # 뱀이 화면 안에 있을 때만 프레임 추가
        if active_segments > 0:
            frames.append(img)

    # 5. GIF 저장 (프레임 속도: 100ms로 조절하여 가독성 확보)
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
