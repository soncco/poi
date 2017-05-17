from django.conf.urls import url, include

from rest_framework import routers
from . import views

#router = routers.DefaultRouter()


app_name = 'base'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.the_login, name = 'the_login'),
    url(r'^logout/$', views.the_logout, name = 'the_logout'),
    #url(r'^api/base/', include(router.urls)),
]
