from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from .models import Template
from .forms import TemplateForm
from staff.models import Staff


def get_current_staff(request):
    """현재 로그인한 스텝 정보 반환"""
    staff_user = request.session.get('staff_user')
    if not staff_user:
        return None
    return Staff.objects.filter(no=staff_user['no']).first()


def check_login_required(view_func):
    """세션 기반 로그인 확인 데코레이터"""
    def wrapped_view(request, *args, **kwargs):
        if not request.session.get('staff_user'):
            return redirect('/auth/login/?next=' + request.path)
        return view_func(request, *args, **kwargs)
    return wrapped_view


class TemplateListView(ListView):
    """템플리트 목록 뷰"""
    model = Template
    template_name = 'template/template_list.html'
    context_object_name = 'templates'
    paginate_by = 20  # 한 페이지당 20개 항목 표시

    def dispatch(self, request, *args, **kwargs):
        # 세션 기반 로그인 확인
        if not request.session.get('staff_user'):
            return redirect('/auth/login/?next=' + request.path)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()

        # 수신대상 필터링
        nReceiver = self.request.GET.get('nReceiver')
        if nReceiver and nReceiver != 'all':
            queryset = queryset.filter(nReceiver=int(nReceiver))

        # 구분 필터링
        nType = self.request.GET.get('nType')
        if nType and nType != 'all':
            queryset = queryset.filter(nType=int(nType))

        # 검색어 필터링
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(sTitle__icontains=search) | Q(sContent__icontains=search)
            )

        return queryset.order_by('-no')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nReceiver'] = self.request.GET.get('nReceiver', 'all')
        context['nType'] = self.request.GET.get('nType', 'all')
        context['search'] = self.request.GET.get('search', '')

        # 현재 스텝 정보 추가
        context['current_staff'] = get_current_staff(self.request)

        # choices 전달
        context['receiver_choices'] = Template.RECEIVER_CHOICES
        context['type_choices'] = Template.TYPE_CHOICES

        # 전체 템플릿 개수와 필터된 결과 개수
        context['total_count'] = Template.objects.count()

        # paginator를 통해 필터된 개수 가져오기
        if hasattr(context.get('paginator', None), 'count'):
            context['filtered_count'] = context['paginator'].count
        else:
            context['filtered_count'] = context['total_count']

        return context


class TemplateCreateView(CreateView):
    """템플리트 추가 뷰"""
    model = Template
    form_class = TemplateForm
    template_name = 'template/template_form.html'
    success_url = reverse_lazy('template:template_list')

    def dispatch(self, request, *args, **kwargs):
        # 세션 기반 로그인 확인
        if not request.session.get('staff_user'):
            return redirect('/auth/login/?next=' + request.path)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, '템플리트가 성공적으로 추가되었습니다.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_staff'] = get_current_staff(self.request)
        return context


class TemplateUpdateView(UpdateView):
    """템플리트 수정 뷰"""
    model = Template
    form_class = TemplateForm
    template_name = 'template/template_form.html'
    success_url = reverse_lazy('template:template_list')

    def dispatch(self, request, *args, **kwargs):
        # 세션 기반 로그인 확인
        if not request.session.get('staff_user'):
            return redirect('/auth/login/?next=' + request.path)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, '템플리트가 성공적으로 수정되었습니다.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_staff'] = get_current_staff(self.request)
        return context


class TemplateDetailView(DetailView):
    """템플리트 상세 뷰"""
    model = Template
    template_name = 'template/template_detail.html'
    context_object_name = 'template'

    def dispatch(self, request, *args, **kwargs):
        # 세션 기반 로그인 확인
        if not request.session.get('staff_user'):
            return redirect('/auth/login/?next=' + request.path)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 사용횟수 증가
        self.object.increment_use_count()
        # 현재 스텝 정보 추가
        context['current_staff'] = get_current_staff(self.request)
        return context


def template_delete(request, pk):
    """템플리트 삭제"""
    # 세션 기반 로그인 확인
    if not request.session.get('staff_user'):
        return redirect('/auth/login/?next=' + request.path)

    template = get_object_or_404(Template, pk=pk)
    if request.method == 'POST':
        template.delete()
        messages.success(request, '템플리트가 성공적으로 삭제되었습니다.')
        return redirect('template:template_list')

    # 컨텍스트에 current_staff 추가
    context = {
        'template': template,
        'current_staff': get_current_staff(request)
    }
    return render(request, 'template/template_confirm_delete.html', context)