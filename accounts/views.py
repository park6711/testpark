from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.urls import reverse
import json

from .models import CustomUser, AuthSession
from .naver_auth import naver_auth, jandi_webhook


class LoginView(View):
    """로그인 페이지"""

    def get(self, request):
        # 이미 로그인된 경우 메인 페이지로 리다이렉트
        if request.user.is_authenticated:
            return redirect('demo:index')  # 메인 페이지 URL

        return render(request, 'accounts/login.html')


class NaverLoginView(View):
    """네이버 로그인 시작"""

    def get(self, request):
        try:
            login_url, state = naver_auth.get_login_url()
            # state를 세션에 저장 (추가 보안)
            request.session['naver_state'] = state
            return redirect(login_url)

        except Exception as e:
            messages.error(request, f"네이버 로그인 연결에 실패했습니다: {str(e)}")
            return redirect('accounts:login')


class NaverCallbackView(View):
    """네이버 로그인 콜백 처리"""

    def get(self, request):
        code = request.GET.get('code')
        state = request.GET.get('state')
        error = request.GET.get('error')

        # 에러 처리
        if error:
            messages.error(request, f"네이버 로그인이 취소되었습니다: {error}")
            return redirect('accounts:login')

        if not code or not state:
            messages.error(request, "필수 파라미터가 없습니다.")
            return redirect('accounts:login')

        # state 검증 (추가 보안)
        session_state = request.session.get('naver_state')
        if session_state != state:
            messages.error(request, "잘못된 요청입니다.")
            return redirect('accounts:login')

        try:
            # 네이버 인증 처리
            success, user_info, error_message = naver_auth.process_naver_login(code, state)

            if not success:
                messages.error(request, error_message)
                return redirect('accounts:login')

            # 사용자 정보 추출
            naver_id = user_info['id']
            naver_email = user_info['email']
            naver_name = user_info['name']

            # 이미 네이버 ID로 연동된 사용자인지 확인
            existing_user = CustomUser.objects.filter(naver_id=naver_id).first()
            if existing_user:
                # 기존 연동 사용자 → 즉시 로그인
                login(request, existing_user)
                messages.success(request, f"환영합니다, {existing_user.name}님!")

                # 잔디 알림 발송
                jandi_webhook.send_login_success(existing_user.name, existing_user.email)

                return redirect('demo:index')

            # 이메일로 기존 사용자 찾기
            existing_email_user = CustomUser.objects.filter(email=naver_email).first()
            if not existing_email_user:
                # DB에 이메일이 없음 → 가입 불가
                messages.error(
                    request,
                    f"등록되지 않은 이메일입니다: {naver_email}\n"
                    "관리자에게 계정 등록을 요청해주세요."
                )
                return redirect('accounts:login')

            # 기존 사용자 있음 → 인증번호 발송
            auth_code = existing_email_user.generate_auth_code()

            # 잔디로 인증번호 발송
            if jandi_webhook.send_auth_code(existing_email_user.email, auth_code):
                # 인증 세션 생성
                session_key = request.session.session_key
                if not session_key:
                    request.session.save()
                    session_key = request.session.session_key

                AuthSession.create_session(
                    session_key=session_key,
                    naver_data=user_info,
                    auth_code=auth_code
                )

                messages.info(request, "인증번호가 잔디로 발송되었습니다. 확인해주세요.")
                return redirect('accounts:verify_code')

            else:
                messages.error(request, "인증번호 발송에 실패했습니다. 다시 시도해주세요.")
                return redirect('accounts:login')

        except Exception as e:
            messages.error(request, f"로그인 처리 중 오류가 발생했습니다: {str(e)}")
            return redirect('accounts:login')

        finally:
            # 세션에서 state 제거
            if 'naver_state' in request.session:
                del request.session['naver_state']


class VerifyCodeView(View):
    """인증번호 입력 페이지"""

    def get(self, request):
        # 로그인된 경우 메인으로
        if request.user.is_authenticated:
            return redirect('demo:index')

        # 인증 세션 확인
        session_key = request.session.session_key
        if not session_key:
            messages.error(request, "세션이 만료되었습니다. 다시 로그인해주세요.")
            return redirect('accounts:login')

        auth_session = AuthSession.objects.filter(
            session_key=session_key,
            is_verified=False
        ).first()

        if not auth_session or auth_session.is_expired():
            messages.error(request, "인증 세션이 만료되었습니다. 다시 로그인해주세요.")
            return redirect('accounts:login')

        return render(request, 'accounts/verify_code.html', {
            'user_email': auth_session.naver_data.get('email', '')
        })

    def post(self, request):
        auth_code = request.POST.get('auth_code', '').strip()

        if not auth_code:
            messages.error(request, "인증번호를 입력해주세요.")
            return self.get(request)

        session_key = request.session.session_key
        if not session_key:
            messages.error(request, "세션이 만료되었습니다.")
            return redirect('accounts:login')

        try:
            # 인증 세션 조회
            auth_session = AuthSession.objects.filter(
                session_key=session_key,
                auth_code=auth_code,
                is_verified=False
            ).first()

            if not auth_session or auth_session.is_expired():
                messages.error(request, "인증번호가 틀렸거나 만료되었습니다.")
                return self.get(request)

            # 네이버 데이터에서 사용자 정보 추출
            naver_data = auth_session.naver_data
            naver_email = naver_data['email']

            # 기존 사용자 찾기
            user = CustomUser.objects.filter(email=naver_email).first()
            if not user:
                messages.error(request, "사용자를 찾을 수 없습니다.")
                return redirect('accounts:login')

            # 네이버 정보 업데이트
            user.naver_id = naver_data['id']
            user.naver_email = naver_data['email']
            user.naver_name = naver_data['name']
            user.is_naver_linked = True
            user.clear_auth_code()  # 인증번호 정리
            user.save()

            # 인증 세션 완료 처리
            auth_session.is_verified = True
            auth_session.user = user
            auth_session.save()

            # 로그인 처리
            login(request, user)
            messages.success(request, f"환영합니다, {user.name}님! 네이버 계정이 연동되었습니다.")

            # 잔디 알림 발송
            jandi_webhook.send_login_success(user.name, user.email)

            return redirect('demo:index')

        except Exception as e:
            messages.error(request, f"인증 처리 중 오류가 발생했습니다: {str(e)}")
            return self.get(request)


@require_http_methods(["POST"])
def resend_auth_code(request):
    """인증번호 재발송 (AJAX)"""
    if request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': '이미 로그인되어 있습니다.'})

    session_key = request.session.session_key
    if not session_key:
        return JsonResponse({'success': False, 'message': '세션이 없습니다.'})

    try:
        auth_session = AuthSession.objects.filter(
            session_key=session_key,
            is_verified=False
        ).first()

        if not auth_session:
            return JsonResponse({'success': False, 'message': '인증 세션을 찾을 수 없습니다.'})

        naver_email = auth_session.naver_data['email']
        user = CustomUser.objects.filter(email=naver_email).first()

        if not user:
            return JsonResponse({'success': False, 'message': '사용자를 찾을 수 없습니다.'})

        # 새 인증번호 생성
        new_auth_code = user.generate_auth_code()

        # 잔디로 발송
        if jandi_webhook.send_auth_code(user.email, new_auth_code):
            # 세션 업데이트
            auth_session.auth_code = new_auth_code
            auth_session.save()

            return JsonResponse({'success': True, 'message': '인증번호가 재발송되었습니다.'})
        else:
            return JsonResponse({'success': False, 'message': '인증번호 발송에 실패했습니다.'})

    except Exception as e:
        return JsonResponse({'success': False, 'message': f'오류: {str(e)}'})


class LogoutView(View):
    """로그아웃"""

    def post(self, request):
        logout(request)
        messages.success(request, "로그아웃되었습니다.")
        return redirect('accounts:login')

    def get(self, request):
        # GET 요청도 허용 (링크로 로그아웃 가능)
        return self.post(request)
