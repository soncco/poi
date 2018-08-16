from .models import Producto, Clasificador
from rest_framework import serializers

class ClasificadorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Clasificador
        fields = ('id', 'cadena', 'descripcion',)


class ProductoSerializer(serializers.HyperlinkedModelSerializer):
    clasificador = ClasificadorSerializer()
    class Meta:
        model = Producto
        fields = ('id', 'descripcion', 'precio', 'clasificador', 'unidad_medida')

