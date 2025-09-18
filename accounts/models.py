from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta


class CustomUser(AbstractUser):
    """
    네이버 소셜 로그인을 지원하는 확장 사용자 모델
    """
    # 기본 필드들 (사전 입력됨)
    email = models.EmailField(unique=True, help_text="네이버 이메일 매칭용")
    name = models.CharField(max_length=100, help_text="실명")
    phone = models.CharField(max_length=20, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)

    # 네이버 소셜 로그인 필드들
    naver_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True,
        help_text="네이버 사용자 고유 ID"
    )
    naver_email = models.EmailField(
        blank=True,
        null=True,
        help_text="네이버에서 받은 이메일"
    )
    naver_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="네이버에서 받은 이름"
    )

    # 인증번호 관련 필드들
    auth_code = models.CharField(
        max_length=6,
        blank=True,
        null=True,
        help_text="6자리 인증번호"
    )
    auth_code_expires = models.DateTimeField(
        blank=True,
        null=True,
        help_text="인증번호 만료시간"
    )

    # 메타 정보
    is_naver_linked = models.BooleanField(
        default=False,
        help_text="네이버 계정 연동 여부"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'name']

    class Meta:
        db_table = 'auth_user'
        verbose_name = '사용자'
        verbose_name_plural = '사용자들'

    def __str__(self):
        return f"{self.email} - {self.name}"

    def generate_auth_code(self):
        """6자리 인증번호 생성"""
        import random
        import string

        self.auth_code = ''.join(random.choices(string.digits, k=6))
        self.auth_code_expires = timezone.now() + timedelta(minutes=5)
        self.save()
        return self.auth_code

    def is_auth_code_valid(self, code):
        """인증번호 유효성 검사"""
        return (
            self.auth_code == code and
            self.auth_code_expires and
            timezone.now() <= self.auth_code_expires
        )

    def clear_auth_code(self):
        """인증번호 정리"""
        self.auth_code = None
        self.auth_code_expires = None
        self.save()


class AuthSession(models.Model):
    """
    네이버 로그인 과정에서의 임시 세션 데이터 (일반 사용자 + 스텝)
    """
    LOGIN_TYPE_CHOICES = [
        ('normal', '일반 로그인'),
        ('staff', '스텝 로그인'),
    ]

    session_key = models.CharField(
        max_length=255,
        unique=True,
        help_text="세션 키"
    )
    login_type = models.CharField(
        max_length=10,
        choices=LOGIN_TYPE_CHOICES,
        default='normal',
        help_text="로그인 타입"
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="연결된 사용자 (일반 로그인)"
    )
    staff_email = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="스텝 이메일 (스텝 로그인)"
    )
    naver_data = models.JSONField(
        help_text="네이버에서 받은 데이터 임시 저장"
    )
    auth_code = models.CharField(
        max_length=6,
        help_text="발송된 인증번호"
    )
    expires_at = models.DateTimeField(
        help_text="세션 만료시간"
    )
    is_verified = models.BooleanField(
        default=False,
        help_text="인증 완료 여부"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'auth_session'
        verbose_name = '인증 세션'
        verbose_name_plural = '인증 세션들'
        ordering = ['-created_at']

    def __str__(self):
        return f"Session {self.session_key} - {self.created_at}"

    def is_expired(self):
        """세션 만료 확인"""
        return timezone.now() > self.expires_at

    @classmethod
    def create_session(cls, session_key, naver_data, auth_code, login_type='normal', staff_email=None):
        """새 인증 세션 생성"""
        return cls.objects.create(
            session_key=session_key,
            login_type=login_type,
            naver_data=naver_data,
            auth_code=auth_code,
            staff_email=staff_email,
            expires_at=timezone.now() + timedelta(minutes=10)
        )
