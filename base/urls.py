from django.conf.urls import url, include

from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'unidades', views.UnidadViewSet)


app_name = 'base'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.the_login, name = 'the_login'),
    url(r'^logout/$', views.the_logout, name = 'the_logout'),
    url(r'^password$', views.my_password, name = 'my_password'),
    url(r'^usuarios$', views.usuarios, name = 'usuarios'),
    url(r'^usuario$', views.usuario, name = 'usuario'),
    url(r'^usuario/(?P<id>.*)$', views.usuario_editar, name = 'usuario_editar'),
    url(r'^opciones$', views.opciones, name = 'opciones'),
    url(r'^alineacion$', views.alineacion, name = 'alineacion'),

    url(r'^api/base/', include(router.urls)),
    url(r'^api/base/unidad/filter/$', views.UnidadFilterViewSet.as_view()),
]
