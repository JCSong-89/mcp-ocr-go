import pandas as pd
from io import StringIO # 문자열을 파일처럼 다루기 위해
import re # 정규표현식 사용을 위해 import

def make_csv_to_excel(csv_text, excel_file_name):
  try:
    # 1. CSV 텍스트 클리닝: 앞뒤 코드 펜스 및 불필요한 공백/줄바꿈 제거
    cleaned_csv_text = re.sub(r'^\s*```[a-zA-Z]*\n?|\n?```\s*$', '', csv_text).strip()
    print("--- 클리닝된 CSV (일부) ---")
    print('\n'.join(cleaned_csv_text.splitlines()[:2])) # 앞 두 줄만 확인
    print("-------------------------")

    # 2. 클리닝된 CSV -> DataFrame
    csv_data = StringIO(cleaned_csv_text)
    df = pd.read_csv(csv_data)

    # 3. 엑셀 파일 경로 및 시트 이름
    excel_path = f'{excel_file_name}.xlsx'
    sheet_name = 'TestCases'

    # 4. ExcelWriter 생성 (xlsxwriter 엔진 사용)
    writer = pd.ExcelWriter(excel_path, engine='xlsxwriter')

    # 5. DataFrame 데이터를 엑셀에 쓰기 (★ 중요: pandas 헤더는 쓰지 않음, 1행부터 데이터 시작)
    df.to_excel(writer, sheet_name=sheet_name, index=False, header=False, startrow=1)

    # 6. xlsxwriter 워크북 및 워크시트 객체 얻기
    workbook = writer.book
    worksheet = writer.sheets[sheet_name]

    # 7. 헤더 서식 정의 (xlsxwriter 방식)
    header_format = workbook.add_format({
        'bold': True,           # 굵게
        'bg_color': '#E5E4E2',  # 밝은 회색 배경
        'border': 1,            # 얇은 테두리 (1)
        'align': 'center',      # 가로 가운데 정렬
        'valign': 'vcenter'     # 세로 가운데 정렬
    })

    # 8. 헤더 행(0행)에 컬럼명 직접 쓰기 + 서식 적용
    # enumerate를 사용하여 컬럼 번호(0부터 시작)와 컬럼 값(이름)을 함께 가져옴
    for col_num, value in enumerate(df.columns.values):
        # worksheet.write(행, 열, 값, 서식)
        worksheet.write(0, col_num, value, header_format)

    # 9. 컬럼 너비 조절 (xlsxwriter 방식)
    for idx, col in enumerate(df.columns): # 각 컬럼에 대해 반복
        series = df[col]
        # 헤더 길이와 데이터 최대 길이 중 더 큰 값을 기준으로 너비 계산
        max_len = max((
            series.astype(str).map(len).max(),  # 데이터 값의 최대 길이
            len(str(series.name))               # 헤더(컬럼명)의 길이
        )) + 2  # 약간의 여유 공간 추가
        worksheet.set_column(idx, idx, max_len) # set_column(시작열, 끝열, 너비)

    # 10. 변경사항 저장 (xlsxwriter는 close() 또는 save() 필수)
    writer.close() # close()가 save()를 포함하므로 close() 사용 권장

    print(f"xlsxwriter 엔진으로 엑셀 파일 저장 완료: {excel_path}")

  except pd.errors.EmptyDataError:
      print("오류: CSV 데이터가 비어 있습니다.")
  except ImportError:
      print("오류: xlsxwriter 라이브러리가 설치되지 않았습니다. 'pip install xlsxwriter'를 실행해주세요.")
  except Exception as e:
      print(f"xlsxwriter 처리 중 오류 발생: {e}")