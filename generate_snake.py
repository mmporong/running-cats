import os

# 1. 파일명 형식 맞춤: 01.png, 02.png ... 20.png
BASE_URL = "https://raw.githubusercontent.com/mmporong/running-cats/main"
# zfill(2)를 사용해 1을 01로 만듭니다.
CAT_IMAGES = [f"{BASE_URL}/{str(i).zfill(2)}.png" for i in range(1, 21)]

def generate_svg():
    width = 800
    height = 150
    # 경로 설정 (화면 밖에서 들어와서 밖으로 나가는 연출)
    path_data = "M -100,60 H 900" 

    svg_header = f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">\n'
    svg_footer = '</svg>'
    
    content = '  <rect width="100%" height="100%" fill="transparent" />\n'
    
    for i, img_url in enumerate(CAT_IMAGES):
        delay = i * 0.5 # 고양이 사이의 간격
        duration = "10s" # 이동 속도
        
        content += f'''
  <image href="{img_url}" width="50" height="50">
    <animateMotion path="{path_data}" dur="{duration}" begin="{delay}s" repeatCount="indefinite" />
  </image>'''

    with open("cat-snake.svg", "w") as f:
        f.write(svg_header + content + svg_footer)

if __name__ == "__main__":
    generate_svg()