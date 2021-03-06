# -*- coding: utf-8 -*-
"""poi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from base import urls

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^', include('base.urls')),
    url(r'^', include('plan.urls')),
    url(r'^', include('reporte.urls')),
    url(r'^', include('cuadro.urls')),

    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]

admin.site.site_header = 'POI - Administración'
admin.site.site_title = 'POI - Administración'

handler404 = 'base.views.handler404'
handler500 = 'base.views.handler500'
handler403 = 'base.views.handler403'
