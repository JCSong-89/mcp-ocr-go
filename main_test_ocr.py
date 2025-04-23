import os, sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from ocr_module.ocr import image_ocr_to_text
from pdf_to_image_parser.pdf_parser import pdf_to_images_pymupdf

output_folder = 'test_page'
output_dic = pdf_to_images_pymupdf('원카드토탈서비스지원시스템구축_요구사항정의서_2016년_사전규격_최종 1.pdf', output_folder, dpi=300) # DPI는 필요에 따라 조절
total_page_num = output_dic["last_page_num"]
test_path = []

for i in range(total_page_num):
  test_path.append(f"{output_folder}/{output_dic['last_page_image_path']}{i + 1}.png")

result = image_ocr_to_text(test_path)

file_path = 'output_list.txt'
# 파일을 쓰기 모드('w')로 열기 (인코딩 지정 권장)
with open(file_path, 'w', encoding='utf-8') as f:
    # 방법 1: 각 요소를 새 줄에 저장
    for item in result:
        f.write(str(item) + '\n') # str()로 문자열 변환 후 줄바꿈(\n) 추가

    # # 방법 2: 구분자(예: 쉼표)로 연결하여 한 줄에 저장
    # f.write(','.join(map(str, my_list))) # map()으로 모든 요소를 str 변환 후 join

print(f"리스트가 '{file_path}' 파일로 저장되었습니다.")