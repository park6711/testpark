#!/usr/bin/env python3
# 특정 UUID 데이터 직접 확인

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

# 기본 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_PATH = os.path.join(BASE_DIR, 'seongdal-a900e25ac63c.json')

# 구글 스프레드시트 ID
SPREADSHEET_ID = '157_Z_ZGX2_bE_vgtZnrWtB6BxCBJOigNqaaAAMGJ1NM'

# 서비스 계정 인증 설정
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

try:
    # 인증
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_PATH, scope)
    client = gspread.authorize(credentials)

    # 스프레드시트 열기
    sheet = client.open_by_key(SPREADSHEET_ID)
    worksheet = sheet.worksheet('[견적의뢰 접수]')

    # 모든 데이터 가져오기
    all_data = worksheet.get_all_values()

    # 특정 UUID 찾기
    target_uuid = 'c266464d-250a-4e3f-8b80-dd0572f227c5'

    for i, row in enumerate(all_data[7:], start=8):  # 8행부터 시작
        if len(row) > 34 and row[34] == target_uuid:
            print(f"✅ {target_uuid} 데이터 찾음! (행 {i})")
            print(f"  A(타임스탬프): {row[0]}")
            print(f"  B(카페글): {row[1]}")
            print(f"  C(지정): {row[2]}")
            print(f"  D(별명): {row[3]}")
            print(f"  E(네이버ID): {row[4]}")
            print(f"  F(이름): {row[5]}")
            print(f"  G(전화): {row[6]}")
            print(f"  H(게시글): {row[7]}")
            print(f"  I(지역): {row[8]}")
            print(f"  J(공사예정일): {row[9]}")
            print(f"  K(공사내용): {row[10][:100] if len(row) > 10 else 'N/A'}...")
            print(f"  L: {row[11] if len(row) > 11 else 'N/A'}")
            print(f"  M: {row[12] if len(row) > 12 else 'N/A'}")
            print(f"  AH(참조링크): {row[33] if len(row) > 33 else 'N/A'}")
            print(f"  AI(UUID): {row[34]}")
            break
    else:
        print(f"UUID {target_uuid}를 찾을 수 없습니다")

except Exception as e:
    print(f"오류: {e}")
    import traceback
    traceback.print_exc()