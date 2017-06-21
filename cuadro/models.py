# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from decimal import Decimal
from django.contrib.auth.models import User

@python_2_unicode_compatible
class Producto(models.Model):
    descripcion = models.TextField()

    def __str__(self):
        return self.descripcion

@python_2_unicode_compatible
class Clasificador(models.Model):
    cadena = models.CharField(max_length = 20)
    descripcion = models.CharField(max_length = 255)

    class Meta:
        verbose_name = ('Clasificador')
        verbose_name_plural = ('Clasificadores')

    def __str__(self):
        return self.cadena

class Cuadro(models.Model):
  actividad = models.OneToOneField('plan.Actividad')
  sec_func = models.CharField(max_length = 4, default='', blank=True)
  creado_por = models.ForeignKey(User)
  total = models.DecimalField(max_digits = 11, decimal_places = 2, default = Decimal('0.00'))


class CuadroDetalle(models.Model):
  pertenece_a = models.ForeignKey(Cuadro)
  unidad_medida = models.CharField(max_length=100)
  producto = models.ForeignKey(Producto)
  clasificador = models.ForeignKey(Clasificador)
  p1 = models.FloatField(default=0)
  p2 = models.FloatField(default=0)
  p3 = models.FloatField(default=0)
  p4 = models.FloatField(default=0)
  p5 = models.FloatField(default=0)
  p6 = models.FloatField(default=0)
  p7 = models.FloatField(default=0)
  p8 = models.FloatField(default=0)
  p9 = models.FloatField(default=0)
  p10 = models.FloatField(default=0)
  p11 = models.FloatField(default=0)
  p12 = models.FloatField(default=0)
  total_cantidades = models.FloatField(default=0)
  precio = models.DecimalField(max_digits = 11, decimal_places = 2, default = Decimal('0.00'))
  total = models.DecimalField(max_digits = 11, decimal_places = 2, default = Decimal('0.00'))