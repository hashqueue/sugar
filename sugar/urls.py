"""sugar URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.conf.urls.static import static
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from . import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/<str:version>/system/', include('system.urls')),
    path('api/<str:version>/pm/', include('pm.urls')),
    path('api/<str:version>/', include('device.urls')),
    path('api/<str:version>/', include('task.urls')),
    # YOUR PATTERNS
    path('api/<str:version>/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/<str:version>/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/<str:version>/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# 用户媒体文件只在debug模式下生效
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 自定义 500服务器错误 响应体数据结构
handler500 = 'utils.drf_utils.custom_server_error_500_handler.server_error'
