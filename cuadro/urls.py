from django.conf.urls import url, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'productos', views.ProductoViewSet)

app_name = 'cuadro'
urlpatterns = [
    #url(r'^plan/nuevo/$', views.plan, name='plan'),
    url(r'^cuadro/nuevo/(?P<id>.*)$', views.nuevo_cuadro, name='nuevo_cuadro'),

    url(r'^api/cuadro/', include(router.urls)),
    url(r'^api/cuadro/producto/filter/$', views.ProductoFilterViewSet.as_view()),
    
]
