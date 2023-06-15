"""
URL configuration for config project.

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
from typing import re

from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path, include
from django.urls import re_path
from django.views.static import serve
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


schema_view = get_schema_view(
   openapi.Info(
      title="RSK API",
      default_version='v1',
      description="Test description",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
   )


urlpatterns = i18n_patterns(
    path('admin/', admin.site.urls),
    path('account/', include('apps.account.urls')),
    path('operators/', include('apps.operators.urls')),
    path('talon/', include('apps.talon.urls')),
    # path('administrator/', include('apps.administrator.urls')),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
)
urlpatterns += [path('i18n/', include('django.conf.urls.i18n')),]
urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)
urlpatterns += staticfiles_urlpatterns()