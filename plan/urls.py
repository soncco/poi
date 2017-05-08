from django.conf.urls import url

from . import views

app_name = 'plan'
urlpatterns = [
    url(r'^plan/nuevo/$', views.plan, name='plan'),
    url(r'^plan/lista/$', views.planes, name='planes'),
    url(r'^plan/lista/json/$', views.planes_json, name='planes_json'),
    url(r'^plan/ver/(?P<id>.*)$', views.ver_plan, name='ver_plan'),
    url(r'^plan/borrar/(?P<id>.*)$', views.borrar_plan, name='borrar_plan'),
]
