from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.conf import settings
from django.db import connection
import platform
import os

def home(request):
    """
    React 앱 또는 데모 홈페이지 뷰
    """
    # React 빌드 파일이 있으면 React 앱 서빙
    react_index = os.path.join(settings.STATIC_ROOT, 'react', 'index.html')
    if os.path.exists(react_index):
        with open(react_index, 'r', encoding='utf-8') as f:
            html_content = f.read()
            # 경로를 Django static URL에 맞게 조정
            # JS/CSS 파일은 이미 /static/ 경로에 있으므로 그대로 유지
            # 기타 asset 파일들만 수정
            html_content = html_content.replace('href="/favicon.ico"', f'href="{settings.STATIC_URL}react/favicon.ico"')
            html_content = html_content.replace('href="/logo192.png"', f'href="{settings.STATIC_URL}react/logo192.png"')
            html_content = html_content.replace('href="/manifest.json"', f'href="{settings.STATIC_URL}react/manifest.json"')
            return HttpResponse(html_content)

    # React 빌드가 없으면 데모 페이지 표시
    context = {
        'title': '🚀 TestPark Django 테스트 환경',
        'message': '안녕하세요! 카페24 실서버에서 실행되는 Django 5.1.1 애플리케이션입니다.',
        'current_time': timezone.now(),
        'python_version': platform.python_version(),
        'server_info': {
            'platform': platform.platform(),
            'architecture': platform.architecture()[0],
            'processor': platform.processor() or 'Unknown',
        }
    }
    return render(request, 'demo/home.html', context)

def api_status(request):
    """
    API 상태 확인 엔드포인트
    """
    data = {
        'status': 'OK',
        'message': 'Django API가 정상적으로 작동중입니다',
        'timestamp': timezone.now().isoformat(),
        'version': '1.0.0'
    }
    return HttpResponse(
        f"""
        <h2>🚀 API Status</h2>
        <p><strong>상태:</strong> {data['status']}</p>
        <p><strong>메시지:</strong> {data['message']}</p>
        <p><strong>시간:</strong> {data['timestamp']}</p>
        <p><strong>버전:</strong> {data['version']}</p>
        <hr>
        <a href="/">← 홈으로 돌아가기</a>
        """,
        content_type='text/html; charset=utf-8'
    )

def health_check(request):
    """
    헬스체크 엔드포인트 - Docker HEALTHCHECK에서 사용
    데이터베이스 연결 상태를 확인하여 애플리케이션의 실제 가용성을 판단
    """
    try:
        # 데이터베이스 연결 확인
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

        return JsonResponse({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': timezone.now().isoformat()
        }, status=200)

    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=503)
