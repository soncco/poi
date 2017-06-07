from rest_framework import routers, serializers, viewsets

from .models import Unidad

class UnidadSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Unidad
        fields = ('pk', 'nombre', 'abreviatura',)
