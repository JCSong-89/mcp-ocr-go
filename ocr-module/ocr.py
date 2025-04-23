import cv2
import easyocr
import numpy as np
import math # 기울기 계산에 필요
import matplotlib.pyplot as plt
import sys,os
from PIL import ImageFont, Image, ImageDraw

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

total_trust_point = 0
get_text_count = 0
ocr_text = []

def putText(cv_img, text, x, y, color=(0, 0, 0), font_size=22):
  # Colab이 아닌 Local에서 수행 시에는 gulim.ttc 를 사용하면 됩니다.
  # font = ImageFont.truetype("fonts/gulim.ttc", font_size)
  font = ImageFont.truetype('/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf', font_size)
  img = Image.fromarray(cv_img)
   
  draw = ImageDraw.Draw(img)
  draw.text((x, y), text, font=font, fill=color)
 
  cv_img = np.array(img)
  
  return cv_img


def deskew_function(binary_image):
    """
    이진 이미지의 기울기를 감지하고 보정합니다.
    :param binary_image: 기울기를 보정할 이진 이미지 (흰색 텍스트, 검은색 배경 권장)
    :return: 기울기가 보정된 이미지
    """
    # OpenCV 4.x 버전에서는 findContours가 2개의 값만 반환합니다.
    # 이미지의 텍스트가 검은색이고 배경이 흰색이라면 반전시킵니다.
    # Otsu's thresholding은 보통 흰색 객체/검은색 배경을 반환하므로,
    # 입력 이미지에 따라 아래 라인의 주석 처리를 결정해야 할 수 있습니다.
    inverted_image = cv2.bitwise_not(binary_image)
    # contours, _ = cv2.findContours(inverted_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # 흰색 텍스트, 검은색 배경 이미지에서 컨투어 찾기
    contours, _ = cv2.findContours(inverted_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        print("기울기 보정: 컨투어를 찾지 못했습니다.")
        return binary_image # 컨투어가 없으면 원본 반환

    # 가장 큰 컨투어(면적 기준)를 찾습니다. (텍스트 블록으로 가정)
    largest_contour = max(contours, key=cv2.contourArea)

    # 최소 면적 경계 사각형을 계산합니다.
    min_area_rect = cv2.minAreaRect(largest_contour)
    # min_area_rect는 ((중심_x, 중심_y), (너비, 높이), 회전 각도) 튜플을 반환합니다.
    # 각도는 [-90, 0) 범위입니다.

    angle = min_area_rect[-1]
    print(f"기울기 보정: 감지된 각도 = {angle:.2f}도")

    # 각도 조정: OpenCV의 minAreaRect 각도는 너비와 높이 정의에 따라 달라질 수 있습니다.
    # 각도가 -45도보다 작으면 90도를 더해 일반적인 기울기 각도로 조정합니다.
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle # 시계 반대 방향 회전을 위해 부호 반전

    # 이미지 중심 계산
    (h, w) = binary_image.shape[:2]
    center = (w // 2, h // 2)

    # 회전 행렬 계산
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

    # 아핀 변환(회전) 적용
    # borderValue를 (0,0,0) (검은색)으로 설정하여 회전 후 빈 공간을 채웁니다.
    rotated_image = cv2.warpAffine(binary_image, rotation_matrix, (w, h),
                                   flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0))

    print(f"기울기 보정: {angle:.2f}도 만큼 이미지를 회전했습니다.")
    return rotated_image

# EasyOCR 리더 초기화 (예: 영어와 한국어 사용)
# gpu=False 옵션은 GPU가 없거나 VRAM이 부족할 경우 CPU를 사용하도록 합니다.
reader = easyocr.Reader(['ko', 'en'], gpu=False)

# 이미지 파일 경로
image_path = './ocr-module/5371578.800000012_image.png' # 실제 이미지 파일 경로로 변경하세요.

# OpenCV로 이미지 읽기
image = cv2.imread(image_path)

if image is None:
    print(f"오류: 이미지 파일을 찾을 수 없거나 읽을 수 없습니다: {image_path}")
else:
    print("이미지 로딩 완료. 전처리를 시작합니다...")

    # --- 이미지 전처리 단계 ---

    # 1. 그레이스케일 변환
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    print("1. 그레이스케일 변환 완료.")

    # 2. 이진화 (Otsu's Thresholding 사용)
    # Otsu's 방법은 이미지 히스토그램을 분석하여 최적의 임계값을 자동으로 결정합니다.
    # 배경과 텍스트 간의 대비가 명확하지 않거나 조명이 불균일할 때 유용합니다.
    ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    print(f"2. Otsu's 이진화 완료 (결정된 임계값: {ret}).")

    # (선택 사항) 추가 전처리 단계 예시:
    # 노이즈 제거 (예: Gaussian Blur) - 필요에 따라 활성화
    blur = cv2.GaussianBlur(thresh, (5,5), 0)
    print(" (선택) 가우시안 블러 적용 완료.")
    preprocessed_image = blur # 블러 적용 시 이 변수 사용

    # 기울기 보정 (Deskewing) - 복잡하며 별도의 함수 구현 필요
    deskewed_image = deskew_function(thresh) # 기울기 보정 함수 호출 (구현 필요)
    print(" (선택) 기울기 보정 적용 완료.")
    preprocessed_image = deskewed_image # 기울기 보정 적용 시 이 변수 사용

    # 현재 예제에서는 이진화된 이미지를 최종 전처리 결과로 사용합니다.
    preprocessed_image = thresh

    # 전처리된 이미지 확인 (선택 사항)
    plt.imshow(preprocessed_image, cmap='gray')
    plt.title('Preprocessed Image')
    plt.show()

    # --- EasyOCR 텍스트 추출 ---
    print("EasyOCR 텍스트 추출을 시작합니다...")
    # EasyOCR은 NumPy 배열 형태의 이미지를 직접 처리할 수 있습니다.
    results = reader.readtext(preprocessed_image)
    print("EasyOCR 텍스트 추출 완료.")

    # --- 결과 출력 ---
    print("\n--- 추출된 텍스트 ---")
    if not results:
        print("텍스트를 찾지 못했습니다.")
    else:
        for (bbox, text, prob) in results:
            print(f"텍스트: {text} (신뢰도: {prob:.4f})")
            ocr_text.append(text)
            trust_point = float(f'{prob:.4f}')
            total_trust_point += trust_point
            get_text_count = get_text_count + 1 

            # 원본 이미지에 경계 상자 그리기
            (tl, tr, br, bl) = bbox

            if type(tl) == type([]) or type(tl) == type(()):
                tl = (int(tl[0]), int(tl[1]))
                tr = (int(tr[0]), int(tr[1]))
                br = (int(br[0]), int(br[1]))
                bl = (int(bl[0]), int(bl[1]))
            else:
                tl = (int(tl), int(tl[1]))
                tr = (int(tr), int(tr[1]))
                br = (int(br), int(br[1]))
                bl = (int(bl), int(bl[1]))

            cv2.rectangle(image, tl, br, (0, 255, 0), 2) # 초록색 사각형
            #cv2.putText(image, text, (tl[0], tl[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            image = putText(image, text, tl[0], tl[1] - 10, (255, 0, 0), 12)

    # (선택 사항) 결과 이미지 보여주기
    output_image_path = 'ocr_result.png'
    cv2.imwrite(output_image_path, image)
    print(f"\n결과 이미지가 '{output_image_path}'로 저장되었습니다.")
    print(f'"총 점수: {trust_point} \ 총 텍스트: {get_text_count}')
    trust_point = trust_point / get_text_count
    print(f"총합 신뢰도: {trust_point}")
    print(f"종합 데이터: \n {ocr_text}")

  
