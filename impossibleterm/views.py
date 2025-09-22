from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from datetime import timedelta
from .models import ImpossibleTerm
from .forms import ImpoForm

# Create your views here.

def get_current_staff(request):
    """현재 로그인한 스텝 정보 반환"""
    from staff.models import Staff
    staff_user = request.session.get('staff_user')
    if not staff_user:
        return None
    return Staff.objects.filter(no=staff_user['no']).first()


class ImpoIndexView(View):
    """Impo 앱 메인 페이지"""

    def get(self, request):
        return HttpResponse("ImpossibleTerm 앱이 생성되었습니다!")


class ImpoListView(ListView):
    """공사 불가능 기간 목록 페이지"""

    model = ImpossibleTerm
    template_name = 'impossibleterm/impo_list.html'
    context_object_name = 'impos'
    paginate_by = 10
    ordering = ['-no']  # 최신순 정렬

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = '공사 불가능 기간 목록'

        # 로그인 및 권한 확인
        staff_user = self.request.session.get('staff_user')
        current_staff = get_current_staff(self.request)

        if not staff_user:
            context['not_logged_in'] = True
            context['impos'] = []
            context['stats'] = {'total': 0, 'active': 0, 'inactive': 0}
            return context

        context['current_staff'] = current_staff
        context['staff_user'] = staff_user

        today = self.get_today()
        context['today'] = today

        # 통계 정보 추가
        active_impos = ImpossibleTerm.objects.filter(dateStart__lte=today, dateEnd__gte=today).count()
        pending_impos = ImpossibleTerm.objects.filter(dateStart__gt=today).count()
        ended_impos = ImpossibleTerm.objects.filter(dateEnd__lt=today).count()

        context['stats'] = {
            'ended': ended_impos,      # 해제된 공사 불가능 기간
            'active': active_impos,    # 현재 적용 중
            'pending': pending_impos   # 예정된 공사 불가능 기간
        }

        return context

    def get_queryset(self):
        """로그인한 사용자만 데이터 반환"""
        if not self.request.session.get('staff_user'):
            return ImpossibleTerm.objects.none()
        return super().get_queryset()

    def get_today(self):
        """오늘 날짜 반환 (한국 시간 기준)"""
        from django.utils import timezone
        return timezone.localtime().date()


class ImpoCreateView(View):
    """공사 불가능 기간 추가 페이지"""

    def get(self, request):
        """공사 불가능 기간 추가 폼 표시"""
        # 로그인 확인
        if not request.session.get('staff_user'):
            messages.error(request, '로그인이 필요합니다.')
            return redirect('accounts:login')

        current_staff = get_current_staff(request)
        form = ImpoForm()

        # 현재 스텝 닉네임을 기본값으로 설정
        if current_staff:
            staff_nick = getattr(current_staff, 'sNick', None) or getattr(current_staff, 'sName', '알 수 없는 스텝')
            form.fields['sWorker'].initial = staff_nick

        # 회사 데이터를 템플릿에 직접 전달
        company_choices = form.get_company_choices()

        context = {
            'form': form,
            'title': '공사 불가능 기간 추가',
            'current_staff': current_staff,
            'staff_user': request.session.get('staff_user'),
            'company_choices': company_choices,
        }

        return render(request, 'impossibleterm/impo_form.html', context)

    def post(self, request):
        """공사 불가능 기간 추가 처리"""
        # 로그인 확인
        if not request.session.get('staff_user'):
            messages.error(request, '로그인이 필요합니다.')
            return redirect('accounts:login')

        current_staff = get_current_staff(request)
        form = ImpoForm(request.POST)

        if form.is_valid():
            impo = form.save(commit=False)
            # 현재 스텝 닉네임을 설정자로 자동 설정
            if current_staff:
                staff_nick = getattr(current_staff, 'sNick', None) or getattr(current_staff, 'sName', '알 수 없는 스텝')
                impo.sWorker = staff_nick
            impo.save()
            messages.success(request, f'공사 불가능 기간이 성공적으로 추가되었습니다. (업체번호: {impo.noCompany})')
            return redirect('impossibleterm:impo_list')
        else:
            messages.error(request, '입력 정보를 확인해주세요.')

        # 회사 데이터를 템플릿에 직접 전달
        company_choices = form.get_company_choices()

        context = {
            'form': form,
            'title': '공사 불가능 기간 추가',
            'current_staff': current_staff,
            'staff_user': request.session.get('staff_user'),
            'company_choices': company_choices,
        }

        return render(request, 'impossibleterm/impo_form.html', context)


class ImpoEditView(View):
    """공사 불가능 기간 수정 페이지"""

    def get(self, request, impo_id):
        """공사 불가능 기간 수정 폼 표시"""
        # 로그인 확인
        if not request.session.get('staff_user'):
            messages.error(request, '로그인이 필요합니다.')
            return redirect('accounts:login')

        current_staff = get_current_staff(request)
        impo = get_object_or_404(ImpossibleTerm, no=impo_id)
        form = ImpoForm(instance=impo)

        # 회사 데이터를 템플릿에 직접 전달
        company_choices = form.get_company_choices()

        context = {
            'form': form,
            'impo': impo,
            'title': f'공사 불가능 기간 수정 ({impo.get_company_name()})',
            'current_staff': current_staff,
            'staff_user': request.session.get('staff_user'),
            'company_choices': company_choices,
        }

        return render(request, 'impossibleterm/impo_form.html', context)

    def post(self, request, impo_id):
        """공사 불가능 기간 수정 처리"""
        # 로그인 확인
        if not request.session.get('staff_user'):
            messages.error(request, '로그인이 필요합니다.')
            return redirect('accounts:login')

        current_staff = get_current_staff(request)
        impo = get_object_or_404(ImpossibleTerm, no=impo_id)
        form = ImpoForm(request.POST, instance=impo)

        if form.is_valid():
            updated_impo = form.save(commit=False)
            # 현재 스텝 닉네임을 설정자로 자동 설정
            if current_staff:
                staff_nick = getattr(current_staff, 'sNick', None) or getattr(current_staff, 'sName', '알 수 없는 스텝')
                updated_impo.sWorker = staff_nick
            updated_impo.save()
            messages.success(request, f'공사 불가능 기간 #{updated_impo.no}이 성공적으로 수정되었습니다.')
            return redirect('impossibleterm:impo_list')
        else:
            messages.error(request, '입력 정보를 확인해주세요.')

        # 회사 데이터를 템플릿에 직접 전달
        company_choices = form.get_company_choices()

        context = {
            'form': form,
            'impo': impo,
            'title': f'공사 불가능 기간 수정 ({impo.get_company_name()})',
            'current_staff': current_staff,
            'staff_user': request.session.get('staff_user'),
            'company_choices': company_choices,
        }

        return render(request, 'impossibleterm/impo_form.html', context)