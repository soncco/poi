from django.conf.urls import url

from . import views

app_name = 'reporte'
urlpatterns = [
    url(r'^plan/imprimir/(?P<id>.*)$', views.imprimir_plan, name='imprimir_plan'),
    url(r'^cuadro/imprimir/(?P<id>.*)$', views.imprimir_cuadro, name='imprimir_cuadro'),

    # Excel
    url(r'^reporte/excel/dependencia$', views.reporte_dependencia_excel, name='reporte_dependencia_excel'),
    url(r'^cuadro/excel$', views.cuadro_excel, name='cuadro_excel'),
]
