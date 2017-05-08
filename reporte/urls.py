from django.conf.urls import url

from . import views

app_name = 'reporte'
urlpatterns = [
    url(r'^plan/imprimir/(?P<id>.*)$', views.imprimir_plan, name='imprimir_plan'),
]
