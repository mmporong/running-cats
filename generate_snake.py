import base64
import os

def generate_svg():
    # 1. 01.png ~ 20.png 파일을 찾아서 데이터로 변환
    encoded_images = []
    for i in range(1, 21):
        file_name = f"{str(i).zfill(2)}.png"
        # 파일이 존재하는지 확인 (경로 디버깅용)
        if os.path.exists(file_name):
            with open(file_name, "rb") as f:
                data = base64.b64encode(f.read()).decode("utf-8")
                encoded_images.append(f"data:image/png;base64,{data}")
        else:
            print(f"Warning: {file_name} not found!")

    # 2. SVG 생성 로직
    width = 800
    height = 150
    path_data = "M -100,75 H 900" # 가로로 가로지르는 경로

    svg_header = f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">\n'
    svg_footer = '</svg>'
    content = '  <rect width="100%" height="100%" fill="transparent" />\n'
    
    # 이미지가 하나도 없을 경우 대비
    if not encoded_images:
        content += '  <text x="10" y="20" fill="red">No PNG files found in the directory!</text>'
    
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
