from .models import Producto, Clasificador
from rest_framework import serializers

class ProductoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Producto
        fields = ('id', 'descripcion', 'precio',)

class ClasificadorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Clasificador
        fields = ('id', 'cadena', 'descripcion',)
