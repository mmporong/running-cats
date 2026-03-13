import base64
import os

def generate_svg():
    # 1. 이미지들을 Base64로 변환하여 리스트에 담기
    encoded_images = []
    for i in range(1, 21):
        file_path = f"{str(i).zfill(2)}.png"
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                data = base64.b64encode(f.read()).decode("utf-8")
                encoded_images.append(f"data:image/png;base64,{data}")

    width = 800
    height = 150
    path_data = "M -100,75 H 900" 

    svg_header = f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">\n'
    svg_footer = '</svg>'
    content = '  <rect width="100%" height="100%" fill="transparent" />\n'
    
    # 2. 인코딩된 데이터를 SVG에 삽입
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
