import os, sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import requests
import config.config as config
import json
import pandas as pd
from io import StringIO # 문자열을 파일처럼 다루기 위해
import re # 정규표현식 사용을 위해 import

from ocr_module.ocr import image_ocr_to_text
from pdf_to_image_parser.pdf_parser import pdf_to_images_pymupdf

output_folder = 'test_page'
output_dic = pdf_to_images_pymupdf('원카드토탈서비스지원시스템구축_요구사항정의서_2016년_사전규격_최종 1.pdf', output_folder, dpi=300) # DPI는 필요에 따라 조절
total_page_num = output_dic["last_page_num"]
test_path = []

for i in range(total_page_num):
  test_path.append(f"{output_folder}/{output_dic['last_page_image_path']}{i + 1}.png")

result = image_ocr_to_text(test_path)

