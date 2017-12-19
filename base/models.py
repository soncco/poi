# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from decimal import Decimal


@python_2_unicode_compatible
class UnidadOrganica(models.Model):
    nombre = models.CharField(max_length=255)
    especial = models.BooleanField(default=False)
    actividades = models.BooleanField(default=False)
    techo = models.DecimalField(max_digits = 19, decimal_places = 5, default = Decimal('0.000'))

    class Meta:
        verbose_name=u'Unidad orgánica'
        verbose_name_plural=u'Unidades orgánicas'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

@python_2_unicode_compatible
class Unidad(models.Model):
    pertenece_a = models.ForeignKey(UnidadOrganica)
    nombre = models.CharField(max_length=255)
    abreviatura = models.CharField(max_length=20, default='')

    class Meta:
        verbose_name='Unidad'
        verbose_name_plural='Unidades'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

@python_2_unicode_compatible
class AsignacionPresupuestal(models.Model):
    fuente = models.CharField(max_length = 100)
    rubro = models.CharField(max_length = 255)

    class Meta:
        verbose_name = (u'Asignación presupuestal')
        verbose_name_plural = ('Asignaciones presupuestales')

    def __str__(self):
        return self.rubro