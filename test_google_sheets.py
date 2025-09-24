#!/usr/bin/env python3
# 구글 스프레드시트 접속 테스트

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
    # 서비스 계정 인증정보 로드
    print(f"인증 파일 경로: {CREDENTIALS_PATH}")
    print(f"파일 존재 여부: {os.path.exists(CREDENTIALS_PATH)}")

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        CREDENTIALS_PATH, scope)

    # gspread 클라이언트 생성
    client = gspread.authorize(credentials)
    print("✅ 구글 인증 성공!")

    # 스프레드시트 열기
    sheet = client.open_by_key(SPREADSHEET_ID)
    print(f"✅ 스프레드시트 열기 성공: {sheet.title}")

    # 모든 워크시트 목록 출력
    print("\n📋 워크시트 목록:")
    worksheets = sheet.worksheets()
    for i, ws in enumerate(worksheets):
        print(f"  {i+1}. {ws.title}")

    # [견적의뢰 접수] 워크시트의 데이터 확인
    target_sheet = None
    for ws in worksheets:
        if ws.title == '[견적의뢰 접수]':
            target_sheet = ws
            break

    if target_sheet:
        ws = target_sheet
        print(f"\n📊 '[견적의뢰 접수]' 워크시트 데이터 확인:")

        # 8행부터 10개 행만 가져와보기
        data = ws.get_all_values()
        if len(data) > 7:
            print(f"  전체 행 수: {len(data)}")
            print(f"  8행 컬럼 수: {len(data[7])}")
            print(f"  8행 데이터 (첫 10개 컬럼): {data[7][:10] if data[7] else 'Empty'}")

            # 9행 데이터도 확인 (실제 데이터)
            if len(data) > 8:
                print(f"\n  9행 데이터 (실제 데이터):")
                row = data[8]
                print(f"    타임스탬프(A): {row[0] if len(row) > 0 else 'N/A'}")
                print(f"    지정여부(B): {row[1] if len(row) > 1 else 'N/A'}")
                print(f"    별명(C): {row[2] if len(row) > 2 else 'N/A'}")
                print(f"    네이버ID(D): {row[3] if len(row) > 3 else 'N/A'}")
                print(f"    이름(E): {row[4] if len(row) > 4 else 'N/A'}")
                print(f"    전화(F): {row[5] if len(row) > 5 else 'N/A'}")
                print(f"    의뢰게시글(G): {row[6] if len(row) > 6 else 'N/A'}")
                print(f"    공사지역(H): {row[7] if len(row) > 7 else 'N/A'}")
                print(f"    공사예정일(I): {row[8] if len(row) > 8 else 'N/A'}")
                print(f"    공사내용(J): {row[9][:50] if len(row) > 9 else 'N/A'}...")

            # AI 컬럼(35번째) 확인
            if len(data[7]) > 34:
                print(f"\n  AI 컬럼(UUID) 값 (8행): {data[7][34]}")
                if len(data) > 8 and len(data[8]) > 34:
                    print(f"  AI 컬럼(UUID) 값 (9행): {data[8][34]}")
            else:
                print(f"  AI 컬럼이 없습니다 (컬럼 수: {len(data[7])})")
        else:
            print("  데이터가 8행까지 없습니다.")

except FileNotFoundError:
    print(f"❌ 인증 파일을 찾을 수 없습니다: {CREDENTIALS_PATH}")
except Exception as e:
    print(f"❌ 오류 발생: {str(e)}")
    import traceback
    traceback.print_exc()