import base64
import os

def generate_svg():
    # 1. 파일 찾기 및 로그 기록
    encoded_images = []
    found_files = []
    
    # 현재 디렉토리의 모든 파일 목록 출력 (디버깅용)
    all_files = os.listdir('.')
    
    for i in range(1, 21):
        # 01.png, 02.png ... 형식 확인
        file_name = f"{str(i).zfill(2)}.png"
        
        if os.path.exists(file_name):
            with open(file_name, "rb") as f:
                data = base64.b64encode(f.read()).decode("utf-8")
                encoded_images.append(f"data:image/png;base64,{data}")
                found_files.append(file_name)
        else:
            print(f"File not found: {file_name}")

    # 2. SVG 생성
    width = 800
    height = 150
    path_data = "M -100,75 H 900"

    svg_header = f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">\n'
    svg_footer = '</svg>'
    
    # 배경
    content = '  <rect width="100%" height="100%" fill="transparent" />\n'
    
    # 🌟 만약 이미지를 하나도 못 찾았다면 에러 메시지 표시
    if not encoded_images:
        content += f'  <text x="10" y="50" fill="red" font-size="20">Error: No PNGs found! Found: {", ".join(all_files[:5])}...</text>'
    else:
        for i, base64_data in enumerate(encoded_images):
            delay = i * 0.6
            duration = "12s"
            content += f'''
  <image xlink:href="{base64_data}" width="50" height="50" y="-25">
    <animateMotion path="{path_data}" dur="{duration}" begin="{delay}s" repeatCount="indefinite" />
  </image>'''

    with open("cat-snake.svg", "w") as f:
        f.write(svg_header + content + svg_footer)

if __name__ == "__main__":
    generate_svg()
