import os
import requests
from PIL import Image, ImageDraw

def get_real_contributions():
    token = os.getenv("GH_TOKEN")
    username = "mmporong"
    
    # 토큰이 없을 경우를 대비한 가짜 데이터 (Mock Data)
    mock_grid = [[(i + j) % 5 for j in range(52)] for i in range(7)]
    
    if not token:
        print("Warning: GH_TOKEN not found. Using mock data.")
        return mock_grid

    # GraphQL 쿼리: 최근 1년치 잔디 데이터 요청
    query = """
    query($username:String!) {
      user(login:$username) {
        contributionsCollection {
          contributionCalendar {
            weeks {
              contributionDays { contributionCount }
            }
          }
        }
      }
    }
    """
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.post("https://api.github.com/graphql", json={'query': query, 'variables': {'username': username}}, headers=headers)
        data = response.json()
        if 'errors' in data:
            print(f"GraphQL Error: {data['errors']}")
            return mock_grid
            
        weeks = data['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
        
        # 7행 52열 매트릭스 생성
        grid = []
        for r in range(7):
            row = []
            for w in weeks:
                if r < len(w['contributionDays']):
                    count = w['contributionDays'][r]['contributionCount']
                    # 커밋 수에 따른 색상 레벨 결정 (0~4)
                    level = 0 if count == 0 else (1 if count < 3 else (2 if count < 6 else (3 if count < 10 else 4)))
                    row.append(level)
                else: row.append(0)
            grid.append(row)
        return grid
    except Exception as e:
        print(f"API Error: {e}")
        return mock_grid

def create_cat_snake_gif():
    # 진짜 데이터를 가져옵니다. 에러 시 가짜 데이터를 반환합니다.
    data = get_real_contributions()
    cat_imgs = []
    # 파일명이 01.png, 02.png ... 형식인지 확인하세요!
    for i in range(1, 21):
        name = f"{str(i).zfill(2)}.png"
        if os.path.exists(name):
            # 🌟 핵심 수정: 고양이를 12x12 셀 크기에 딱 맞춰 스케일링
            cat_imgs.append(Image.open(name).convert("RGBA").resize((12, 12)))
    
    if not cat_imgs:
        print("Error: No cat images found in the directory!")
        return

    # S자 이동 경로 (뱀 게임 특유의 이동)
    path = []
    for col in range(52):
        row_range = range(7) if col % 2 == 0 else range(6, -1, -1)
        for row in row_range:
            path.append((col, row))

    frames = []
    # 4칸씩 건너뛰며 프레임 생성 (애니메이션 속도 조절)
    for f in range(0, len(path) + 20, 3):
        # 배경색: 깃허브 다크모드 색상 (#0d1117)
        img = Image.new("RGBA", (820, 160), (13, 17, 23, 255))
        draw = ImageDraw.Draw(img)
        
        # 🌟 정밀 그리드 계산: 셀 12px, 간격 3px
        cell_size = 12
        spacing = 3
        
        # 1. 잔디밭 그리기
        for col in range(52):
            for row in range(7):
                x = col * (cell_size + spacing) + 20
                y = row * (cell_size + spacing) + 20
                
                # 깃허브 다크모드 표준 잔디 색상셋
                colors = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
                color = colors[data[row][col]]
                
                # '먹기' 연출: 고양이가 이미 지나간 좌표는 배경색으로 지움
                for idx in range(max(0, f-20), f):
                    if idx < len(path) and path[idx] == (col, row):
                        color = "#161b22" # 먹힌 자리
                
                draw.rounded_rectangle([x, y, x + cell_size, y + cell_size], radius=2, fill=color)

        # 2. 고양이 기차 그리기
        for i in range(len(cat_imgs)):
            idx = f - i
            if 0 <= idx < len(path):
                c, r = path[idx]
                x = c * (cell_size + spacing) + 20
                y = r * (cell_size + spacing) + 20
                # 고양이 이미지를 캔버스에 정확히 배치
                img.paste(cat_imgs[i], (x, y), cat_imgs[i])
        
        frames.append(img)

    # 3. GIF 저장
    frames[0].save("cat-snake.gif", save_all=True, append_images=frames[1:], duration=70, loop=0, disposal=2)

if __name__ == "__main__":
    create_cat_snake_gif()
