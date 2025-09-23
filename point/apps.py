from django.apps import AppConfig


class PointConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'point'
    verbose_name = '포인트 관리'

    def ready(self):
        """앱이 준비되면 시그널 연결"""
        import point.signals  # noqa: F401
