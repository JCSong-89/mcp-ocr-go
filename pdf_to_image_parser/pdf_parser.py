import fitz  # PyMuPDF 임포트 시 이름은 fitz 입니다.
import os, sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

"""
pdf_to_images_pymupdf(input_pdf, output_folder=output_dir, dpi=300) # DPI는 필요에 따라 조절
"""
def pdf_to_images_pymupdf(pdf_path, output_folder="pdf_images", dpi=300):
    output = {
        'output_folder_path': output_folder,
        'page_image_path': '',
        'last_page_num': 0
    }
    """
    PyMuPDF를 사용하여 PDF의 각 페이지를 이미지 파일로 저장합니다.

    :param pdf_path: 입력 PDF 파일 경로
    :param output_folder: 이미지를 저장할 폴더 경로
    :param dpi: 이미지 해상도 (dots per inch)
    """
    # 출력 폴더 생성
    os.makedirs(output_folder, exist_ok=True)

    try:
        # PDF 파일 열기
        doc = fitz.open(pdf_path)
        print(f"총 {len(doc)} 페이지의 PDF 파일을 열었습니다.")

        # 각 페이지를 순회하며 이미지로 저장
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)  # 페이지 로드

            # DPI 설정을 위한 변환 매트릭스 생성 (zoom factor)
            # 기본 DPI는 72입니다. 원하는 DPI / 72 = zoom factor
            zoom = dpi / 72.0
            mat = fitz.Matrix(zoom, zoom)

            # 페이지를 Pixmap(픽셀 데이터)으로 렌더링
            pix = page.get_pixmap(matrix=mat)

            page_path = f"page_{page_num + 1}.png"

            # 저장할 이미지 파일 경로 설정 (예: page_1.png, page_2.png)
            output_path = os.path.join(output_folder, page_path)

            # Pixmap을 이미지 파일로 저장 (PNG 형식)
            pix.save(output_path)
            print(f"'{output_path}' 저장 완료 (페이지 {page_num + 1}/{len(doc)})")

            output['last_page_image_path'] = 'page_'
            output['last_page_num'] = page_num + 1

        doc.close()
        print("PDF 페이지 이미지 변환 완료.")

        return output

    except Exception as e:
        print(f"오류 발생: {e}")

