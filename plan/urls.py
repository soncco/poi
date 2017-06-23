from django.conf.urls import url

from . import views

app_name = 'plan'
urlpatterns = [
    url(r'^plan/pre/$', views.pre_plan, name='pre_plan'),
    url(r'^plan/nuevo/$', views.plan, name='plan'),
    url(r'^plan/lista/$', views.planes, name='planes'),
    url(r'^plan/lista/json/$', views.planes_json, name='planes_json'),
    url(r'^plan/ver/(?P<id>.*)$', views.ver_plan, name='ver_plan'),
    url(r'^plan/borrar/(?P<id>.*)$', views.borrar_plan, name='borrar_plan'),
    url(r'^plan/aprobar/(?P<id>.*)$', views.aprobar_plan, name='aprobar_plan'),
    url(r'^actividad/guardar/$', views.guardar_actividad, name='guardar_actividad'),
    url(r'^plan/actividades/(?P<id>.*)$', views.actividades, name='actividades'),

    # Informes.
    url(r'^informe/dependiencia/$', views.informe_dependencia, name='informe_dependencia'),
    url(r'^informe/organica/$', views.informe_organica, name='informe_organica'),
    url(r'^informe/institucion/$', views.informe_institucion, name='informe_institucion'),
    url(r'^informe/resumen/$', views.informe_resumen, name='informe_resumen'),
]
