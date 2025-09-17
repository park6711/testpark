from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
import platform

def home(request):
    """
    데모 홈페이지 뷰
    """
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
