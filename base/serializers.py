from rest_framework import routers, serializers, viewsets

from .models import UnidadMedida, AsignacionPresupuestal

class UnidadMedidaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UnidadMedida
        fields = ( 'pk', 'nombre',)


class AsignacionPresupuestalSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AsignacionPresupuestal
        fields = ('url', 'pk', 'rubro', 'fuente',)
