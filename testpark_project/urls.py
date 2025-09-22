"""
URL configuration for testpark_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('accounts.urls')),
    path('staff/', include('staff.urls')),
    path('member/', include('member.urls')),
    path('company/', include('company.urls')),
    path('license/', include('license.urls')),
    path('join/', include('join.urls')),
    path('stop/', include('stop.urls')),
    path('impossibleterm/', include('impossibleterm.urls')),
    path('possiblearea/', include('possiblearea.urls')),
    path('order/', include('order.urls')),
    path('gonggu/', include('gonggu.urls')),
    path('contract/', include('contract.urls')),
    path('evaluation/', include('evaluation.urls')),
    path('template/', include('template.urls')),
    path('point/', include('point.urls')),
    path('companycondition/', include('companycondition.urls')),
    path('', include('demo.urls')),
]

# Static and Media files serving in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
