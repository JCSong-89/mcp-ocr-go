import os, sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import requests
import config.config as config

def get_csv_test_cases_from_llm(text_list):
  prompt ={
   "contents": [{
    "parts":[{"text": 
              f"""
              이 추출된 텍스트를 보고 유의미한 테스트케이스를 만들어줘.
              추출된 텍스트: 
              {text_list}
              **출력 형식:**
              - 반드시 CSV(Comma-Separated Values) 형식으로 출력해줘.
              - 각 데이터는 쉼표(,)로 구분하고, 문자열은 큰따옴표(")로 감싸도 좋아.
              - 다른 설명이나 제목 없이 CSV 데이터만 출력해줘.
              - 첫 번째 행은 다음 헤더(컬럼명)를 포함해야 해:
                "구분", "요구사항", "ID", "테스트 케이스 ID", "테스트 목적", "테스트 전 컨디션", "테스트 절차", "테스트 데이터", "예상 결과"
              - "구분" 컬럼에는 해당 테스트 케이스가 속하는 섹션 제목(예: "기능 공통 사항", "입장 관리", "계좌 발매 관리" 등)을 넣어줘.

              **예시:**
              "구분","요구사항","ID","테스트 케이스 ID","테스트 목적","테스트 전 컨디션","테스트 절차","테스트 데이터","예상 결과"
              "입장 관리","입장 게이트 개선 (레즈런파크 서울)","SFR-002","TC_SFR_002_001","마이카드 인식 확인","게이트 장비에 마이카드 리더기 연결","마이카드 스캔","유효한 마이카드","게이트 정상 작동 및 회원 정보 연동"
              "입장 관리","입장 게이트 개선 (레즈런파크 서울)","SFR-002","TC_SFR_002_002","NFC 인식 확인","게이트 장비에 NFC 리더기 연결","모바일 회원카드 NFC 태깅","유효한 모바일 회원카 드","게이트 정상 작동 및 회원 정보 연동"
              """
              }]
            }]
  }

  response = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={config.API_KEY}", json=prompt)
  csv_text = response.json()['candidates'][0]['content']['parts'][0]['text']

  return csv_text
