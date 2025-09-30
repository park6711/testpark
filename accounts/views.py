from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.urls import reverse
from django.conf import settings
import json
import urllib.parse

from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import CustomUser, AuthSession
from .naver_auth import naver_auth, jandi_webhook
from .serializers import UserSerializer
from staff.models import Staff
from member.models import Member


class LoginView(View):
    """로그인 페이지"""

    def get(self, request):
        # 이미 로그인된 경우 메인 페이지로 리다이렉트
        if request.user.is_authenticated:
            return redirect('demo:home')  # 메인 페이지 URL

        # 현재 선택된 계정 (쿠키에서 읽기)
        current_account = request.COOKIES.get('current_naver_account')
        if current_account:
            try:
                import json
                current_account = json.loads(current_account)
            except:
                current_account = None

        return render(request, 'accounts/login.html', {
            'current_account': current_account,
            'naver_client_id': settings.NAVER_CLIENT_ID
        })


class CompanyNaverLoginView(View):
    """업체(일반) 네이버 로그인 시작"""

    def get(self, request):
        try:
            # 업체용 콜백 URL 생성
            login_url, state = naver_auth.get_login_url(login_type='company')
            # state를 세션에 저장
            request.session['naver_state'] = state
            request.session['login_type'] = 'company'
            return redirect(login_url)

        except Exception as e:
            messages.error(request, f"업체 네이버 로그인 연결에 실패했습니다: {str(e)}")
            return redirect('accounts:login')


class CompanyNaverCallbackView(View):
    """업체(일반) 네이버 로그인 콜백 처리"""

    def get(self, request):
        print(f"[DEBUG] 업체 네이버 콜백 호출 - URL: {request.get_full_path()}")

        code = request.GET.get('code')
        state = request.GET.get('state')
        error = request.GET.get('error')

        print(f"[DEBUG] 콜백 파라미터 - code: {code[:10] if code else None}..., state: {state}, error: {error}")

        # 에러 처리
        if error:
            print(f"[ERROR] 네이버 로그인 에러: {error}")
            messages.error(request, f"네이버 로그인이 취소되었습니다: {error}")
            return redirect('accounts:login')

        if not code or not state:
            print(f"[ERROR] 필수 파라미터 누락 - code: {bool(code)}, state: {bool(state)}")
            messages.error(request, "필수 파라미터가 없습니다.")
            return redirect('accounts:login')

        # state 검증 (추가 보안)
        session_state = request.session.get('naver_state')
        print(f"[DEBUG] State 검증 - session: {session_state}, callback: {state}")

        if session_state != state:
            print(f"[ERROR] State 불일치 - session: {session_state}, callback: {state}")
            messages.error(request, "잘못된 요청입니다.")
            return redirect('accounts:login')

        # 업체 로그인만 처리

        try:
            # 네이버 인증 처리 (state 검증은 이미 완료되었으므로 건너뛰기)
            print(f"[DEBUG] 네이버 인증 처리 시작")
            success, user_info, error_message = naver_auth.process_naver_login(code, state, skip_state_verification=True)

            if not success:
                print(f"[ERROR] 네이버 인증 실패: {error_message}")
                messages.error(request, error_message)
                return redirect('accounts:login')

            print(f"[DEBUG] 네이버 인증 성공 - 사용자: {user_info.get('email', 'NO_EMAIL')}")

            # 사용자 정보 추출
            naver_id = user_info['id']
            naver_email = user_info['email']
            naver_name = user_info['name']

            # 이미 네이버 ID로 연동된 사용자인지 확인
            existing_user = CustomUser.objects.filter(naver_id=naver_id).first()
            if existing_user:
                print(f"[DEBUG] 기존 연동 사용자 로그인: {existing_user.email}")
                # 기존 연동 사용자 → 즉시 로그인
                login(request, existing_user)
                messages.success(request, f"환영합니다, {existing_user.name}님!")

                # 잔디 알림 발송
                jandi_webhook.send_login_success(existing_user.name, existing_user.email)

                return redirect('demo:home')

            # 이메일로 기존 사용자 찾기
            existing_email_user = CustomUser.objects.filter(email=naver_email).first()
            if not existing_email_user:
                print(f"[ERROR] 등록되지 않은 이메일: {naver_email}")
                # DB에 이메일이 없음 → 가입 불가
                messages.error(
                    request,
                    f"등록되지 않은 이메일입니다: {naver_email}\n"
                    "관리자에게 계정 등록을 요청해주세요."
                )
                return redirect('accounts:login')

            print(f"[DEBUG] 기존 사용자 발견, 인증번호 발송: {existing_email_user.email}")

            # 기존 사용자 있음 → 인증번호 발송
            auth_code = existing_email_user.generate_auth_code()

            # 잔디로 인증번호 발송
            if jandi_webhook.send_auth_code(existing_email_user.email, auth_code):
                # 인증 세션 생성
                session_key = request.session.session_key
                if not session_key:
                    request.session.save()
                    session_key = request.session.session_key

                # 기존 인증 세션이 있다면 삭제
                AuthSession.objects.filter(session_key=session_key).delete()

                AuthSession.create_session(
                    session_key=session_key,
                    naver_data=user_info,
                    auth_code=auth_code
                )

                print(f"[DEBUG] 인증번호 발송 성공, 인증 페이지로 리디렉션")
                messages.info(request, "인증번호가 잔디로 발송되었습니다. 확인해주세요.")
                return redirect('accounts:verify_code')

            else:
                print(f"[ERROR] 인증번호 발송 실패")
                messages.error(request, "인증번호 발송에 실패했습니다. 다시 시도해주세요.")
                return redirect('accounts:login')

        except Exception as e:
            print(f"[ERROR] 콜백 처리 중 예외 발생: {str(e)}")
            import traceback
            traceback.print_exc()
            messages.error(request, f"로그인 처리 중 오류가 발생했습니다: {str(e)}")
            return redirect('accounts:login')

        finally:
            # 세션에서 state 제거
            if 'naver_state' in request.session:
                del request.session['naver_state']
            if 'login_type' in request.session:
                del request.session['login_type']
            print(f"[DEBUG] 업체 로그인 세션 정리 완료")



class StaffNaverCallbackView(View):
    """스텝 네이버 로그인 콜백 처리"""

    def get(self, request):
        print(f"[DEBUG] 스텝 네이버 콜백 호출 - URL: {request.get_full_path()}")

        code = request.GET.get('code')
        state = request.GET.get('state')
        error = request.GET.get('error')

        print(f"[DEBUG] 스텝 콜백 파라미터 - code: {code[:10] if code else None}..., state: {state}, error: {error}")

        # 에러 처리
        if error:
            print(f"[ERROR] 스텝 네이버 로그인 에러: {error}")
            messages.error(request, f"스텝 네이버 로그인이 취소되었습니다: {error}")
            return redirect('accounts:login')

        if not code or not state:
            print(f"[ERROR] 필수 파라미터 누락 - code: {bool(code)}, state: {bool(state)}")
            messages.error(request, "필수 파라미터가 없습니다.")
            return redirect('accounts:login')

        # state 검증 (추가 보안)
        session_state = request.session.get('naver_state')
        print(f"[DEBUG] State 검증 - session: {session_state}, callback: {state}")

        if session_state != state:
            print(f"[ERROR] State 불일치 - session: {session_state}, callback: {state}")
            messages.error(request, "잘못된 요청입니다.")
            return redirect('accounts:login')

        try:
            # 스텝 로그인 처리
            return self._handle_staff_login(request, code, state)
        except Exception as e:
            print(f"[ERROR] 스텝 콜백 처리 중 예외 발생: {str(e)}")
            import traceback
            traceback.print_exc()
            messages.error(request, f"스텝 로그인 처리 중 오류가 발생했습니다: {str(e)}")
            return redirect('accounts:login')
        finally:
            # 세션에서 state 제거
            if 'naver_state' in request.session:
                del request.session['naver_state']
            if 'login_type' in request.session:
                del request.session['login_type']
            print(f"[DEBUG] 스텝 로그인 세션 정리 완료")

    def _handle_staff_login(self, request, code, state):
        """스텝 로그인 처리"""
        try:
            print(f"[DEBUG] 스텝 로그인 처리 시작")
            # 네이버 인증 처리 (state 검증은 이미 완료되었으므로 건너뛰기)
            success, user_info, error_message = naver_auth.process_naver_login(code, state, skip_state_verification=True)

            if not success:
                print(f"[ERROR] 스텝 네이버 인증 실패: {error_message}")
                messages.error(request, error_message)
                return redirect('accounts:login')

            print(f"[DEBUG] 스텝 네이버 인증 성공 - 사용자: {user_info.get('email', 'NO_EMAIL')}")

            # 사용자 정보 추출
            naver_id = user_info['id']
            naver_email = user_info['email']
            naver_name = user_info['name']

            # 🔍 Step 1: Staff에서 네이버 ID로 기존 스텝 찾기 (sNaverID0 = naver_id)
            existing_staff = Staff.objects.filter(sNaverID0=naver_id).first()
            if existing_staff:
                print(f"[DEBUG] 기존 연동 스텝 로그인: {existing_staff.sName}")
                # 이미 네이버 ID가 연동된 스텝 → 즉시 로그인
                request.session['staff_user'] = {
                    'no': existing_staff.no,
                    'name': existing_staff.sName,
                    'email': existing_staff.sNaverID,  # sNaverID = naver_email
                    'team': existing_staff.sTeam,
                    'naver_id': existing_staff.sNaverID0,  # sNaverID0 = naver_id
                }
                messages.success(request, f"환영합니다, {existing_staff.sName}님! (스텝 로그인)")
                return redirect('staff:staff_list')

            # 🔍 Step 2: 이메일로 기존 스텝 찾기 (sNaverID = naver_email)
            existing_email_staff = Staff.objects.filter(sNaverID=naver_email).first()

            if not existing_email_staff:
                print(f"[ERROR] 등록되지 않은 스텝 이메일: {naver_email}")
                # Staff 테이블에 해당 이메일이 없음 → 가입 불가
                messages.error(
                    request,
                    f"등록되지 않은 스텝 이메일입니다: {naver_email}\n"
                    "관리자에게 스텝 등록을 요청해주세요."
                )
                return redirect('accounts:login')

            print(f"[DEBUG] 기존 스텝 발견, 인증번호 발송: {existing_email_staff.sName}")

            # 🔗 Step 3: 스텝에 대해 잔디 인증번호 발송 및 인증 요구
            auth_code = existing_email_staff.generate_auth_code()

            # 잔디로 인증번호 발송
            if jandi_webhook.send_auth_code(existing_email_staff.sNaverID, auth_code):
                # 스텝용 인증 세션 생성
                session_key = request.session.session_key
                if not session_key:
                    request.session.save()
                    session_key = request.session.session_key

                # 기존 인증 세션이 있다면 삭제
                AuthSession.objects.filter(session_key=session_key).delete()

                AuthSession.create_session(
                    session_key=session_key,
                    naver_data=user_info,
                    auth_code=auth_code,
                    login_type='staff',
                    staff_email=existing_email_staff.sNaverID
                )

                print(f"[DEBUG] 스텝 인증번호 발송 성공")
                messages.info(request, f"스텝 인증번호가 잔디로 발송되었습니다. ({existing_email_staff.sName}님)")
                return redirect('accounts:verify_code')

            else:
                print(f"[ERROR] 스텝 인증번호 발송 실패")
                messages.error(request, "스텝 인증번호 발송에 실패했습니다. 다시 시도해주세요.")
                return redirect('accounts:login')

        except Exception as e:
            print(f"[ERROR] 스텝 로그인 처리 중 예외 발생: {str(e)}")
            import traceback
            traceback.print_exc()
            messages.error(request, f"스텝 로그인 처리 중 오류가 발생했습니다: {str(e)}")
            return redirect('accounts:login')


class VerifyCodeView(View):
    """인증번호 입력 페이지"""

    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        # 로그인된 경우 메인으로
        if request.user.is_authenticated:
            return redirect('demo:home')

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

        # 로그인 타입에 따라 이메일 표시
        if auth_session.login_type == 'staff':
            display_email = auth_session.staff_email
            login_type_display = "스텝 로그인"
        else:
            display_email = auth_session.naver_data.get('email', '')
            login_type_display = "일반 로그인"

        return render(request, 'accounts/verify_code.html', {
            'user_email': display_email,
            'login_type': login_type_display
        })

    @method_decorator(csrf_exempt)
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

            # 로그인 타입에 따라 처리 분기
            if auth_session.login_type == 'staff':
                return self._handle_staff_verification(request, auth_session)
            else:
                return self._handle_normal_verification(request, auth_session)

        except Exception as e:
            messages.error(request, f"인증 처리 중 오류가 발생했습니다: {str(e)}")
            return self.get(request)

    def _handle_normal_verification(self, request, auth_session):
        """일반 사용자 인증 처리"""
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

        return redirect('demo:home')

    def _handle_staff_verification(self, request, auth_session):
        """스텝 사용자 인증 처리"""
        # 네이버 데이터에서 정보 추출
        naver_data = auth_session.naver_data
        naver_id = naver_data['id']
        staff_email = auth_session.staff_email

        # 스텝 찾기
        staff = Staff.objects.filter(sNaverID=staff_email).first()
        if not staff:
            messages.error(request, "스텝 정보를 찾을 수 없습니다.")
            return redirect('accounts:login')

        # 네이버 ID 연동 및 저장
        staff.sNaverID0 = naver_id
        staff.save()

        # 인증 세션 완료 처리
        auth_session.is_verified = True
        auth_session.save()

        # 스텝 정보를 세션에 저장 (CustomUser와 독립적)
        request.session['staff_user'] = {
            'no': staff.no,
            'name': staff.sName,
            'email': staff.sNaverID,
            'team': staff.sTeam,
            'naver_id': staff.sNaverID0,
        }

        messages.success(request, f"환영합니다, {staff.sName}님! 스텝 네이버 계정이 연동되었습니다.")
        return redirect('staff:staff_list')


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

        # 로그인 타입에 따라 처리 분기
        if auth_session.login_type == 'staff':
            # 스텝 로그인 재발송
            staff = Staff.objects.filter(sNaverID=auth_session.staff_email).first()
            if not staff:
                return JsonResponse({'success': False, 'message': '스텝을 찾을 수 없습니다.'})

            # 새 인증번호 생성
            new_auth_code = staff.generate_auth_code()

            # 잔디로 발송
            if jandi_webhook.send_auth_code(staff.sNaverID, new_auth_code):
                # 세션 업데이트
                auth_session.auth_code = new_auth_code
                auth_session.save()
                return JsonResponse({'success': True, 'message': '스텝 인증번호가 재발송되었습니다.'})
            else:
                return JsonResponse({'success': False, 'message': '스텝 인증번호 발송에 실패했습니다.'})

        else:
            # 일반 사용자 로그인 재발송
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
        # 네이버 세션도 종료할지 여부 확인
        clear_naver_session = request.POST.get('clear_naver_session', 'false') == 'true'
        next_url = request.POST.get('next', None)  # 로그아웃 후 이동할 URL

        # 세션 완전히 정리
        request.session.flush()

        messages.success(request, "로그아웃되었습니다.")

        # 쿠키 삭제
        if next_url:
            response = redirect(next_url)
        else:
            response = redirect('accounts:login')

        response.delete_cookie('current_naver_account')

        # 네이버 세션도 종료하는 경우
        if clear_naver_session:
            # 네이버 로그아웃 페이지로 리다이렉트
            return_url = request.build_absolute_uri('/auth/login/')
            naver_logout_url = f"https://nid.naver.com/nidlogin.logout?returl={return_url}"
            return redirect(naver_logout_url)

        return response

    def get(self, request):
        # GET 요청도 허용 (링크로 로그아웃 가능)
        clear_naver_session = request.GET.get('clear_naver_session', 'false') == 'true'
        next_url = request.GET.get('next', None)  # 로그아웃 후 이동할 URL

        # 세션 완전히 정리
        request.session.flush()

        messages.success(request, "로그아웃되었습니다.")

        # 쿠키 삭제
        if next_url:
            response = redirect(next_url)
        else:
            response = redirect('accounts:login')

        response.delete_cookie('current_naver_account')

        # 네이버 세션도 종료하는 경우
        if clear_naver_session:
            # 네이버 로그아웃 페이지로 리다이렉트
            return_url = request.build_absolute_uri('/auth/login/')
            naver_logout_url = f"https://nid.naver.com/nidlogin.logout?returl={return_url}"
            return redirect(naver_logout_url)

        return response


class StaffNaverLoginView(View):
    """스텝 네이버 로그인 시작"""

    def get(self, request):
        try:
            print(f"[DEBUG] 스텝 로그인 시작")
            # 스텝용 콜백 URL 생성
            login_url, state = naver_auth.get_login_url(login_type='staff')
            print(f"[DEBUG] 스텝 로그인 URL 생성 - state: {state}")
            print(f"[DEBUG] 스텝 로그인 URL: {login_url}")
            # state를 세션에 저장
            request.session['naver_state'] = state
            request.session['login_type'] = 'staff'
            print(f"[DEBUG] 세션에 저장된 state: {request.session.get('naver_state')}")
            return redirect(login_url)

        except Exception as e:
            messages.error(request, f"스텝 네이버 로그인 연결에 실패했습니다: {str(e)}")
            return redirect('accounts:login')


class TestStaffLoginView(View):
    """임시 스텝 로그인 (개발용)"""

    def get(self, request):
        # 임시로 스텝 세션 생성
        request.session['staff_user'] = {
            'no': 1,
            'name': '테스트 스텝',
            'email': 'test@example.com',
            'team': '개발팀',
            'naver_id': 'test_naver_id',
        }
        messages.success(request, "임시 스텝 로그인이 완료되었습니다!")
        return redirect('staff:staff_list')


class TestCompanyLoginView(View):
    """임시 업체 로그인 (개발용)"""

    def get(self, request):
        from .models import CustomUser
        from django.contrib.auth import login

        # 테스트 사용자 생성 또는 조회
        test_user, created = CustomUser.objects.get_or_create(
            email='test@company.com',
            defaults={
                'name': '테스트 업체',
                'is_naver_linked': True,
                'naver_id': 'test_company_id'
            }
        )

        login(request, test_user)
        messages.success(request, f"임시 업체 로그인이 완료되었습니다! ({test_user.name})")
        return redirect('demo:home')


class StaffTempLoginView(View):
    """스텝 임시 로그인 (네이버 콜백 없이)"""

    def get(self, request):
        """임시 스텝 로그인 처리"""
        try:
            from staff.models import Staff

            # 테스트용 스텝 계정 생성 또는 조회
            # 실제 환경에서는 적절한 스텝 계정을 사용해야 함
            staff, created = Staff.objects.get_or_create(
                sNaverID='temp_staff',
                defaults={
                    'sNaverID0': 'temp_staff_id0',
                    'sName': '임시스텝',
                    'sTeam': '개발팀',
                    'sTitle': '임시직급',
                    'sNick': '임시스텝',
                    'sPhone1': '010-0000-0000',
                    'bApproval': True,
                    'nStaffAuthority': 1,  # 스텝 권한
                    'nCompanyAuthority': 1,  # 업체 권한
                }
            )

            # 세션에 스텝 정보 저장
            request.session['staff_user'] = {
                'no': staff.no,
                'name': staff.sName,
                'nick': staff.sNick,
                'naver_id': staff.sNaverID,
                'authority': staff.nStaffAuthority,
                'company_authority': staff.nCompanyAuthority,
            }

            messages.success(request, f'임시 스텝 로그인이 완료되었습니다. (스텝: {staff.sName})')

            # 스텝 메인 페이지로 리다이렉트
            return redirect('/staff/')

        except Exception as e:
            messages.error(request, f"임시 스텝 로그인에 실패했습니다: {str(e)}")
            return redirect('accounts:login')


class NaverCallbackView(View):
    """통합 네이버 로그인 콜백 처리 (업체/스텝 구분은 state로 처리)"""

    def get(self, request):
        print(f"[DEBUG] 통합 네이버 콜백 호출 - URL: {request.get_full_path()}")
        print(f"[DEBUG] 전체 GET 파라미터: {dict(request.GET)}")

        code = request.GET.get('code')
        state = request.GET.get('state')
        error = request.GET.get('error')

        # state에서 로그인 타입 추출
        if state and ':' in state:
            original_state, login_type = state.split(':', 1)
        else:
            original_state = state
            login_type = 'company'

        print(f"[DEBUG] 콜백 파라미터 - code: {code[:10] if code else None}..., state: {original_state}, type: {login_type}, error: {error}")

        # 에러 처리
        if error:
            print(f"[ERROR] 네이버 로그인 에러: {error}")
            messages.error(request, f"네이버 로그인이 취소되었습니다: {error}")
            return redirect('accounts:login')

        if not code or not state:
            print(f"[ERROR] 필수 파라미터 누락 - code: {bool(code)}, state: {bool(state)}")
            messages.error(request, "필수 파라미터가 없습니다.")
            return redirect('accounts:login')

        # state 검증 (추가 보안)
        session_state = request.session.get('naver_state')
        print(f"[DEBUG] State 검증 - session: {session_state}, callback: {state}")

        if session_state != state:
            print(f"[ERROR] State 불일치 - session: {session_state}, callback: {state}")
            messages.error(request, "잘못된 요청입니다.")
            return redirect('accounts:login')

        try:
            # 로그인 타입에 따라 처리 분기
            if login_type == 'unified':
                # 통합 로그인 뷰로 처리 위임
                unified_view = UnifiedNaverCallbackView()
                return unified_view.get(request)
            elif login_type == 'staff':
                return self._handle_staff_login(request, code, state)
            else:
                return self._handle_company_login(request, code, state)
        except Exception as e:
            print(f"[ERROR] 콜백 처리 중 예외 발생: {str(e)}")
            import traceback
            traceback.print_exc()
            messages.error(request, f"로그인 처리 중 오류가 발생했습니다: {str(e)}")
            return redirect('accounts:login')
        finally:
            # 세션에서 state 제거
            if 'naver_state' in request.session:
                del request.session['naver_state']
            if 'login_type' in request.session:
                del request.session['login_type']
            print(f"[DEBUG] 로그인 세션 정리 완료")

    def _handle_company_login(self, request, code, state):
        """업체 로그인 처리"""
        print(f"[DEBUG] 업체 로그인 처리 시작")
        # 네이버 인증 처리 (state 검증은 이미 완료되었으므로 건너뛰기)
        success, user_info, error_message = naver_auth.process_naver_login(code, state, skip_state_verification=True)

        if not success:
            print(f"[ERROR] 네이버 인증 실패: {error_message}")
            messages.error(request, error_message)
            return redirect('accounts:login')

        print(f"[DEBUG] 네이버 인증 성공 - 사용자: {user_info.get('email', 'NO_EMAIL')}")

        # 사용자 정보 추출
        naver_id = user_info['id']
        naver_email = user_info['email']
        naver_name = user_info['name']

        # 이미 네이버 ID로 연동된 사용자인지 확인
        existing_user = CustomUser.objects.filter(naver_id=naver_id).first()
        if existing_user:
            print(f"[DEBUG] 기존 연동 사용자 로그인: {existing_user.email}")
            # 기존 연동 사용자 → 즉시 로그인
            login(request, existing_user)
            messages.success(request, f"환영합니다, {existing_user.name}님!")

            # 잔디 알림 발송
            jandi_webhook.send_login_success(existing_user.name, existing_user.email)

            return redirect('demo:home')

        # 이메일로 기존 사용자 찾기
        existing_email_user = CustomUser.objects.filter(email=naver_email).first()
        if not existing_email_user:
            print(f"[ERROR] 등록되지 않은 이메일: {naver_email}")
            # DB에 이메일이 없음 → 가입 불가
            messages.error(
                request,
                f"등록되지 않은 이메일입니다: {naver_email}\n"
                "관리자에게 계정 등록을 요청해주세요."
            )
            return redirect('accounts:login')

        print(f"[DEBUG] 기존 사용자 발견, 인증번호 발송: {existing_email_user.email}")

        # 기존 사용자 있음 → 인증번호 발송
        auth_code = existing_email_user.generate_auth_code()

        # 잔디로 인증번호 발송
        if jandi_webhook.send_auth_code(existing_email_user.email, auth_code):
            # 인증 세션 생성
            session_key = request.session.session_key
            if not session_key:
                request.session.save()
                session_key = request.session.session_key

            # 기존 인증 세션이 있다면 삭제
            AuthSession.objects.filter(session_key=session_key).delete()

            AuthSession.create_session(
                session_key=session_key,
                naver_data=user_info,
                auth_code=auth_code
            )

            print(f"[DEBUG] 인증번호 발송 성공, 인증 페이지로 리디렉션")
            messages.info(request, "인증번호가 잔디로 발송되었습니다. 확인해주세요.")
            return redirect('accounts:verify_code')

        else:
            print(f"[ERROR] 인증번호 발송 실패")
            messages.error(request, "인증번호 발송에 실패했습니다. 다시 시도해주세요.")
            return redirect('accounts:login')

    def _handle_staff_login(self, request, code, state):
        """스텝 로그인 처리"""
        print(f"[DEBUG] 스텝 로그인 처리 시작")
        # 네이버 인증 처리 (state 검증은 이미 완료되었으므로 건너뛰기)
        success, user_info, error_message = naver_auth.process_naver_login(code, state, skip_state_verification=True)

        if not success:
            print(f"[ERROR] 스텝 네이버 인증 실패: {error_message}")
            messages.error(request, error_message)
            return redirect('accounts:login')

        print(f"[DEBUG] 스텝 네이버 인증 성공 - 사용자: {user_info.get('email', 'NO_EMAIL')}")

        # 사용자 정보 추출
        naver_id = user_info['id']
        naver_email = user_info['email']
        naver_name = user_info['name']

        # 🔍 Step 1: Staff에서 네이버 ID로 기존 스텝 찾기 (sNaverID0 = naver_id)
        existing_staff = Staff.objects.filter(sNaverID0=naver_id).first()
        if existing_staff:
            print(f"[DEBUG] 기존 연동 스텝 로그인: {existing_staff.sName}")
            # 이미 네이버 ID가 연동된 스텝 → 즉시 로그인
            request.session['staff_user'] = {
                'no': existing_staff.no,
                'name': existing_staff.sName,
                'email': existing_staff.sNaverID,  # sNaverID = naver_email
                'team': existing_staff.sTeam,
                'naver_id': existing_staff.sNaverID0,  # sNaverID0 = naver_id
            }
            messages.success(request, f"환영합니다, {existing_staff.sName}님! (스텝 로그인)")
            return redirect('staff:staff_list')

        # 🔍 Step 2: 이메일로 기존 스텝 찾기 (sNaverID = naver_email)
        existing_email_staff = Staff.objects.filter(sNaverID=naver_email).first()

        if not existing_email_staff:
            print(f"[ERROR] 등록되지 않은 스텝 이메일: {naver_email}")
            # Staff 테이블에 해당 이메일이 없음 → 가입 불가
            messages.error(
                request,
                f"등록되지 않은 스텝 이메일입니다: {naver_email}\n"
                "관리자에게 스텝 등록을 요청해주세요."
            )
            return redirect('accounts:login')

        print(f"[DEBUG] 기존 스텝 발견, 인증번호 발송: {existing_email_staff.sName}")

        # 🔗 Step 3: 스텝에 대해 잔디 인증번호 발송 및 인증 요구
        auth_code = existing_email_staff.generate_auth_code()

        # 잔디로 인증번호 발송
        if jandi_webhook.send_auth_code(existing_email_staff.sNaverID, auth_code):
            # 스텝용 인증 세션 생성
            session_key = request.session.session_key
            if not session_key:
                request.session.save()
                session_key = request.session.session_key

            # 기존 인증 세션이 있다면 삭제
            AuthSession.objects.filter(session_key=session_key).delete()

            AuthSession.create_session(
                session_key=session_key,
                naver_data=user_info,
                auth_code=auth_code,
                login_type='staff',
                staff_email=existing_email_staff.sNaverID
            )

            print(f"[DEBUG] 스텝 인증번호 발송 성공")
            messages.info(request, f"스텝 인증번호가 잔디로 발송되었습니다. ({existing_email_staff.sName}님)")
            return redirect('accounts:verify_code')

        else:
            print(f"[ERROR] 스텝 인증번호 발송 실패")
            messages.error(request, "스텝 인증번호 발송에 실패했습니다. 다시 시도해주세요.")
            return redirect('accounts:login')


# REST API Views
class UserListAPIView(generics.ListAPIView):
    """사용자 목록 API"""
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]  # 개발용 - 실제 환경에서는 IsAuthenticated 사용

    def get_queryset(self):
        """활성 사용자만 반환"""
        return CustomUser.objects.filter(is_active=True).order_by('-date_joined')


@api_view(['GET'])
@permission_classes([AllowAny])  # 개발용
def api_status(request):
    """API 상태 확인"""
    return Response({
        'status': 'ok',
        'message': 'TestPark Django API is running',
        'user_count': CustomUser.objects.count(),
        'version': '1.0.0'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_user_profile(request):
    """현재 로그인된 사용자 프로필"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


class UnifiedNaverLoginView(View):
    """통합 네이버 로그인 시작"""

    def get(self, request):
        try:
            # 프롬프트 파라미터 확인 (계정 선택 화면 강제 표시 여부)
            prompt = request.GET.get('prompt')
            # 예상 이메일 (검증용)
            expected_email = request.GET.get('expected')

            # 예상 이메일을 세션에 저장 (콜백에서 검증용)
            if expected_email:
                request.session['expected_email'] = expected_email
                print(f"[DEBUG] 예상 계정 설정: {expected_email}")

            # 통합 콜백 URL 생성
            login_url, state = naver_auth.get_login_url(
                login_type='unified',
                prompt=prompt
            )
            # state를 세션에 저장
            request.session['naver_state'] = state
            request.session['login_type'] = 'unified'
            return redirect(login_url)

        except Exception as e:
            messages.error(request, f"네이버 로그인 연결에 실패했습니다: {str(e)}")
            return redirect('accounts:login')


class SwitchAccountView(View):
    """계정 전환을 위한 중간 페이지 - 네이버 로그아웃을 확실히 처리"""

    def get(self, request):
        """선택한 계정으로 전환하기 위해 네이버 로그아웃 처리"""
        selected_email = request.GET.get('email', '')

        # 네이버 로그아웃 후 OAuth 페이지로 이동
        # auth_type=reauthenticate로 강제 재인증
        oauth_url = request.build_absolute_uri(
            reverse('accounts:unified_naver_login')
        ) + '?prompt=logout'

        return render(request, 'accounts/switch_account.html', {
            'selected_email': selected_email,
            'oauth_url': oauth_url
        })



class UnifiedNaverCallbackView(View):
    """통합 네이버 로그인 콜백 처리 (Staff/Member 자동 구분)"""

    def _save_account_to_cookie(self, response, account_info):
        """로그인한 계정 정보를 쿠키에 저장 (중복 제거)"""
        import json

        # 현재 계정을 쿠키에 저장
        response.set_cookie(
            'current_naver_account',
            json.dumps(account_info),
            max_age=30*24*60*60,  # 30일
            httponly=False  # JavaScript에서 읽을 수 있도록
        )


        return response

    def get(self, request):
        self.request = request  # request 객체를 인스턴스 변수로 저장
        print(f"[DEBUG] 통합 네이버 콜백 호출 - URL: {request.get_full_path()}")

        code = request.GET.get('code')
        state = request.GET.get('state')
        error = request.GET.get('error')

        print(f"[DEBUG] 콜백 파라미터 - code: {code[:10] if code else None}..., state: {state}, error: {error}")

        # 에러 처리
        if error:
            print(f"[ERROR] 네이버 로그인 에러: {error}")
            messages.error(request, f"네이버 로그인이 취소되었습니다: {error}")
            return redirect('accounts:login')

        if not code or not state:
            print(f"[ERROR] 필수 파라미터 누락 - code: {bool(code)}, state: {bool(state)}")
            messages.error(request, "필수 파라미터가 없습니다.")
            return redirect('accounts:login')

        # state 검증 (세션 문제로 임시 완화)
        session_state = request.session.get('naver_state')
        print(f"[DEBUG] State 검증 - session: {session_state}, callback: {state}")

        # 세션 state가 없거나 일치하지 않는 경우 경고만 표시
        if session_state and session_state != state:
            print(f"[WARNING] State 불일치 - session: {session_state}, callback: {state}")
            # 세션 문제로 인한 임시 조치 - 경고만 표시하고 진행
        elif not session_state:
            print(f"[WARNING] 세션에 state가 없음 - callback state: {state}")
            # 세션이 없는 경우도 진행 허용

        try:
            # 네이버 인증 처리
            print(f"[DEBUG] 네이버 인증 처리 시작")
            success, user_info, error_message = naver_auth.process_naver_login(code, state, skip_state_verification=True)

            if not success:
                print(f"[ERROR] 네이버 인증 실패: {error_message}")
                messages.error(request, error_message)
                return redirect('accounts:login')

            print(f"[DEBUG] 네이버 인증 성공 - 사용자: {user_info.get('email', 'NO_EMAIL')}")

            # 사용자 정보 추출
            naver_id = user_info['id']  # return0: 네이버 식별자
            naver_email = user_info['email']  # return1: 로그인 이메일
            naver_name = user_info['name']

            # 🔍 예상 계정 검증
            expected_email = request.session.get('expected_email')
            if expected_email:
                print(f"[DEBUG] 계정 검증 - 예상: {expected_email}, 실제: {naver_email}")

                if expected_email != naver_email:
                    # 잘못된 계정으로 로그인됨 - 재시도 필요
                    print(f"[WARNING] 잘못된 계정으로 로그인! 예상: {expected_email}, 실제: {naver_email}")

                    # 재시도 횟수 확인
                    retry_count = request.session.get('retry_count', 0)
                    if retry_count >= 2:
                        # 2번 이상 실패 시 포기
                        messages.error(request, f"{expected_email} 계정으로 로그인할 수 없습니다. 네이버에서 해당 계정을 선택해주세요.")
                        request.session.pop('expected_email', None)
                        request.session.pop('retry_count', None)
                        return redirect('accounts:login')

                    # 재시도
                    request.session['retry_count'] = retry_count + 1
                    messages.warning(request, f"{expected_email} 계정을 선택해주세요.")

                    # 네이버 로그아웃 페이지로 강제 이동
                    return_url = request.build_absolute_uri(
                        reverse('accounts:unified_naver_login') + f'?expected={expected_email}&prompt=select_account'
                    )
                    logout_url = f"https://nid.naver.com/nidlogin.logout?returl={urllib.parse.quote(return_url)}"
                    return redirect(logout_url)
                else:
                    # 올바른 계정으로 로그인됨
                    print(f"[SUCCESS] 예상한 계정으로 로그인 성공: {naver_email}")
                    request.session.pop('expected_email', None)
                    request.session.pop('retry_count', None)

            # 🔍 Step 1: Staff에서 sNaverID0와 return0(naver_id)가 일치하는 것 찾기
            staff = Staff.objects.filter(sNaverID0=naver_id).first()
            if staff:
                if staff.bApproval:  # 승인된 스텝
                    print(f"[DEBUG] 승인된 스텝 로그인: {staff.sName}")
                    request.session['staff_user'] = {
                        'no': staff.no,
                        'name': staff.sName,
                        'email': staff.sNaverID,
                        'team': staff.sTeam,
                        'naver_id': staff.sNaverID0,
                    }
                    messages.success(request, f"환영합니다, {staff.sName}님!")

                    # 쿠키에 계정 정보 저장
                    response = redirect('order:order_list')  # 의뢰 리스트로 이동
                    self._save_account_to_cookie(response, {
                        'email': staff.sNaverID,
                        'name': staff.sName,
                        'type': 'staff',
                        'naver_id': staff.sNaverID0
                    })
                    return response
                else:  # 미승인 스텝
                    print(f"[DEBUG] 미승인 스텝 로그인 시도: {staff.sName}")
                    error_msg = f"해당 아이디({naver_email})로는 로그인이 불가능합니다. 관리자에게 문의바랍니다."
                    return render(request, 'accounts/login.html', {'error_message': error_msg})

            # 🔍 Step 2: Member에서 sNaverID0와 return0(naver_id)가 일치하는 것 찾기
            member = Member.objects.filter(sNaverID0=naver_id).first()
            if member:
                if member.bApproval:  # 승인된 업체
                    print(f"[DEBUG] 승인된 업체 로그인: {member.sCompanyName}")
                    request.session['member_user'] = {
                        'no': member.no,
                        'company_name': member.sCompanyName,
                        'email': member.sNaverID,
                        'naver_id': member.sNaverID0,
                    }
                    messages.success(request, f"환영합니다, {member.sCompanyName}님!")

                    # 쿠키에 계정 정보 저장
                    response = redirect('member:member_dashboard')  # 업체 대시보드로 이동
                    self._save_account_to_cookie(response, {
                        'email': member.sNaverID,
                        'name': member.sCompanyName,
                        'type': 'member',
                        'naver_id': member.sNaverID0
                    })
                    return response
                else:  # 미승인 업체
                    print(f"[DEBUG] 미승인 업체 로그인 시도: {member.sCompanyName}")
                    error_msg = f"해당 아이디({naver_email})로는 로그인이 불가능합니다. 관리자에게 문의바랍니다."
                    return render(request, 'accounts/login.html', {'error_message': error_msg})

            # 🔍 Step 3: Staff에서 sNaverID(이메일)와 return1(naver_email)이 일치하는 것 찾기
            staff_by_email = Staff.objects.filter(sNaverID=naver_email).first()
            if staff_by_email:
                if staff_by_email.bApproval:  # 승인된 스텝 (첫 네이버 로그인)
                    # sNaverID0에 return0 저장
                    staff_by_email.sNaverID0 = naver_id
                    staff_by_email.save()
                    print(f"[DEBUG] 스텝 첫 네이버 로그인, ID 연동: {staff_by_email.sName}")

                    request.session['staff_user'] = {
                        'no': staff_by_email.no,
                        'name': staff_by_email.sName,
                        'email': staff_by_email.sNaverID,
                        'team': staff_by_email.sTeam,
                        'naver_id': naver_id,
                    }
                    messages.success(request, f"환영합니다, {staff_by_email.sName}님! (첫 네이버 로그인)")

                    # 쿠키에 계정 정보 저장
                    response = redirect('order:order_list')  # 의뢰 리스트로 이동
                    self._save_account_to_cookie(response, {
                        'email': staff_by_email.sNaverID,
                        'name': staff_by_email.sName,
                        'type': 'staff',
                        'naver_id': naver_id
                    })
                    return response
                else:  # 미승인 스텝
                    print(f"[DEBUG] 미승인 스텝 로그인 시도 (이메일): {staff_by_email.sName}")
                    error_msg = f"해당 아이디({naver_email})로는 로그인이 불가능합니다. 관리자에게 문의바랍니다."
                    return render(request, 'accounts/login.html', {'error_message': error_msg})

            # 🔍 Step 4: Member에서 sNaverID(이메일)와 return1(naver_email)이 일치하는 것 찾기
            member_by_email = Member.objects.filter(sNaverID=naver_email).first()
            if member_by_email:
                if member_by_email.bApproval:  # 승인된 업체 (첫 네이버 로그인)
                    # sNaverID0에 return0 저장
                    member_by_email.sNaverID0 = naver_id
                    member_by_email.save()
                    print(f"[DEBUG] 업체 첫 네이버 로그인, ID 연동: {member_by_email.sCompanyName}")

                    request.session['member_user'] = {
                        'no': member_by_email.no,
                        'company_name': member_by_email.sCompanyName,
                        'email': member_by_email.sNaverID,
                        'naver_id': naver_id,
                    }
                    messages.success(request, f"환영합니다, {member_by_email.sCompanyName}님! (첫 네이버 로그인)")

                    # 쿠키에 계정 정보 저장
                    response = redirect('member:member_dashboard')  # 업체 대시보드로 이동
                    self._save_account_to_cookie(response, {
                        'email': member_by_email.sNaverID,
                        'name': member_by_email.sCompanyName,
                        'type': 'member',
                        'naver_id': naver_id
                    })
                    return response
                else:  # 미승인 업체
                    print(f"[DEBUG] 미승인 업체 로그인 시도 (이메일): {member_by_email.sCompanyName}")
                    error_msg = f"해당 아이디({naver_email})로는 로그인이 불가능합니다. 관리자에게 문의바랍니다."
                    return render(request, 'accounts/login.html', {'error_message': error_msg})

            # 등록되지 않은 사용자
            print(f"[ERROR] 등록되지 않은 사용자: {naver_email}")
            error_msg = f"등록되지 않은 계정입니다: {naver_email}\n관리자에게 계정 등록을 요청해주세요."
            return render(request, 'accounts/login.html', {'error_message': error_msg})

        except Exception as e:
            print(f"[ERROR] 통합 콜백 처리 중 예외 발생: {str(e)}")
            import traceback
            traceback.print_exc()
            messages.error(request, f"로그인 처리 중 오류가 발생했습니다: {str(e)}")
            return redirect('accounts:login')

        finally:
            # 세션에서 state 제거
            if 'naver_state' in request.session:
                del request.session['naver_state']
            if 'login_type' in request.session:
                del request.session['login_type']
            print(f"[DEBUG] 로그인 세션 정리 완료")


