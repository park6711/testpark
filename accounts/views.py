from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.urls import reverse
import json

from .models import CustomUser, AuthSession
from .naver_auth import naver_auth, jandi_webhook
from staff.models import Staff


class LoginView(View):
    """로그인 페이지"""

    def get(self, request):
        # 이미 로그인된 경우 메인 페이지로 리다이렉트
        if request.user.is_authenticated:
            return redirect('demo:home')  # 메인 페이지 URL

        return render(request, 'accounts/login.html')


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
        logout(request)
        messages.success(request, "로그아웃되었습니다.")
        return redirect('accounts:login')

    def get(self, request):
        # GET 요청도 허용 (링크로 로그아웃 가능)
        return self.post(request)


class StaffNaverLoginView(View):
    """스텝 네이버 로그인 시작"""

    def get(self, request):
        try:
            # 스텝용 콜백 URL 생성
            login_url, state = naver_auth.get_login_url(login_type='staff')
            # state를 세션에 저장
            request.session['naver_state'] = state
            request.session['login_type'] = 'staff'
            return redirect(login_url)

        except Exception as e:
            messages.error(request, f"스텝 네이버 로그인 연결에 실패했습니다: {str(e)}")
            return redirect('accounts:login')


