#!/usr/bin/env python3
import requests
import json
import sys
from datetime import datetime

print("🔐 Docker Hub Personal Access Token 자동 생성")
print("=" * 50)

# Docker Hub 로그인
print("\n1. Docker Hub 로그인 중...")
login_data = {
    "username": "7171man@naver.com",
    "password": "*jeje4211"
}

try:
    # JWT 토큰 획득
    login_response = requests.post(
        "https://hub.docker.com/v2/users/login",
        json=login_data
    )

    if login_response.status_code != 200:
        print(f"❌ 로그인 실패: {login_response.status_code}")
        print(login_response.text)
        sys.exit(1)

    jwt_token = login_response.json()["token"]
    print("✅ 로그인 성공!")

    # Access Token 생성
    print("\n2. Personal Access Token 생성 중...")

    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }

    # 토큰 이름을 유니크하게 생성
    token_name = f"testpark-auto-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    token_data = {
        "token_label": token_name,
        "scopes": ["repo:admin"]  # 모든 권한
    }

    # Personal Access Token 생성 API 호출
    token_response = requests.post(
        "https://hub.docker.com/v2/access-tokens",
        headers=headers,
        json=token_data
    )

    if token_response.status_code == 201:
        token_info = token_response.json()
        access_token = token_info.get("token")

        if access_token:
            print(f"✅ Access Token 생성 성공!")
            print(f"   이름: {token_name}")
            print("\n" + "=" * 50)
            print("🔑 생성된 Access Token:")
            print("=" * 50)
            print(access_token)
            print("=" * 50)

            # 토큰 파일로 저장
            with open(".docker-token", "w") as f:
                f.write(access_token)
            print("\n✅ 토큰이 .docker-token 파일에 저장되었습니다.")

            print("\n📋 GitHub Secrets 설정 값:")
            print("-" * 50)
            print(f"DOCKER_USERNAME: 7171man")
            print(f"DOCKER_PASSWORD: {access_token}")
            print("-" * 50)

        else:
            print("❌ 토큰 생성은 성공했지만 토큰 값을 받지 못했습니다.")
            print(token_response.text)
    else:
        print(f"❌ Token 생성 실패: {token_response.status_code}")
        print(token_response.text)

except Exception as e:
    print(f"❌ 오류 발생: {str(e)}")
    sys.exit(1)