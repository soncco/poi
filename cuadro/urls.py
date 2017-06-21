from django.conf.urls import url, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'productos', views.ProductoViewSet)
router.register(r'clasificadores', views.ClasificadorViewSet)

app_name = 'cuadro'
urlpatterns = [
    #url(r'^plan/nuevo/$', views.plan, name='plan'),
    url(r'^cuadro/nuevo/(?P<id>.*)$', views.nuevo_cuadro, name='nuevo_cuadro'),
    url(r'^cuadro/editar/(?P<id>.*)$', views.editar_cuadro, name='editar_cuadro'),
    url(r'^cuadro/borrar/(?P<id>.*)$', views.borrar_cuadro, name='borrar_cuadro'),

    # Informes.
    url(r'^informe/cuadro/dependiencia/$', views.informe_dependencia, name='informe_dependencia'),
    url(r'^informe/cuadro/organica/$', views.informe_organica, name='informe_organica'),
    url(r'^informe/cuadro/institucion/$', views.informe_institucion, name='informe_institucion'),

    url(r'^api/cuadro/', include(router.urls)),
    url(r'^api/cuadro/producto/filter/$', views.ProductoFilterViewSet.as_view()),
    url(r'^api/cuadro/clasificador/filter/$', views.ClasificadorFilterViewSet.as_view()),
    
]
