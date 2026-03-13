import os

# 1. 경로 설정
BASE_URL = "https://raw.githubusercontent.com/mmporong/running-cats/main"
CAT_IMAGES = [f"{BASE_URL}/{str(i).zfill(2)}.png" for i in range(1, 21)]

def generate_svg():
    width = 800
    height = 150
    # 경로: 화면 왼쪽 밖에서 오른쪽 끝까지 가로지르는 경로
    path_data = "M -100,75 H 900" 

    # 🌟 핵심 수정: xmlns:xlink 네임스페이스 추가
    svg_header = f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">\n'
    svg_footer = '</svg>'
    
    # 배경 (투명)
    content = '  <rect width="100%" height="100%" fill="transparent" />\n'
    
    for i, img_url in enumerate(CAT_IMAGES):
        delay = i * 0.6 # 고양이 간격 (필요에 따라 조절)
        duration = "12s" # 속도 (필요에 따라 조절)
        
        # 🌟 핵심 수정: xlink:href 사용
        content += f'''
  <image xlink:href="{img_url}" width="50" height="50" y="-25">
    <animateMotion path="{path_data}" dur="{duration}" begin="{delay}s" repeatCount="indefinite" />
  </image>'''

    with open("cat-snake.svg", "w") as f:
        f.write(svg_header + content + svg_footer)

if __name__ == "__main__":
    generate_svg()
