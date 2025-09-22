#!/usr/bin/env python
import os
import sys
import django

# Django 설정
sys.path.append('/Users/sewookpark/Documents/testpark')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testpark_project.settings')
django.setup()

from gonggu.models import Gonggu

def update_gonggu_spost():
    """Gonggu DB의 sPost 필드를 모두 동일한 URL로 업데이트"""

    test_url = "https://cafe.naver.com/pcarpenter/585024"

    # 모든 Gonggu 객체 가져오기
    gonggus = Gonggu.objects.all()

    print(f"총 {gonggus.count()}개의 Gonggu 레코드의 sPost를 업데이트합니다...")

    updated_count = 0
    for gonggu in gonggus:
        gonggu.sPost = test_url
        gonggu.save()
        updated_count += 1
        print(f"Gonggu {gonggu.no}: sPost = {gonggu.sPost}")

    print(f"\n총 {updated_count}개의 Gonggu sPost 필드가 업데이트되었습니다!")
    print(f"모든 sPost 값이 '{test_url}'로 설정되었습니다.")

if __name__ == "__main__":
    update_gonggu_spost()