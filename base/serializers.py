from rest_framework import routers, serializers, viewsets

from .models import AsignacionPresupuestal

class AsignacionPresupuestalSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AsignacionPresupuestal
        fields = ('url', 'pk', 'rubro', 'fuente',)
