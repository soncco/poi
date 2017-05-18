# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from decimal import Decimal
from django.contrib.auth.models import User

#@python_2_unicode_compatible
class Plan(models.Model):
    TIPOS = (
        ('1', 'Trimestral'),
        ('2', 'Mensual'),
    )
    unidad_organica = models.ForeignKey('base.UnidadOrganica')
    area_ejecutora = models.ForeignKey('base.Unidad')
    responsable = models.CharField(max_length=255)
    accion_central = models.TextField()
    objetivo_general_institucional = models.TextField()
    objetivo_especifico_institucional = models.TextField()
    periodo = models.CharField(choices=TIPOS, default='1', max_length=1)
    presupuesto = models.DecimalField(max_digits = 19, decimal_places = 5, default = Decimal('0.000'))
    creado_por = models.ForeignKey(User, default=1)
    aprobado = models.BooleanField(default=False)
    anio = models.CharField(max_length=4, default='')

class Actividad(models.Model):
    TIPOS = (
        ('1', 'Porcentual'),
        ('2', u'Numérico'),
    )
    pertenece_a = models.ForeignKey(Plan)
    tarea_actividad = models.TextField()
    unidad_medida = models.CharField(max_length=100)
    peso = models.FloatField(default=0)
    tipo_t = models.CharField(choices=TIPOS, default='1', max_length=1)
    t1 = models.FloatField(default=0)
    t2 = models.FloatField(default=0)
    t3 = models.FloatField(default=0)
    t4 = models.FloatField(default=0)
    t5 = models.FloatField(default=0)
    t6 = models.FloatField(default=0)
    t7 = models.FloatField(default=0)
    t8 = models.FloatField(default=0)
    t9 = models.FloatField(default=0)
    t10 = models.FloatField(default=0)
    t11 = models.FloatField(default=0)
    t12 = models.FloatField(default=0)
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
    total = models.FloatField(default=0)
    fecha_termino = models.DateField()
    distribucion_presupuestal = models.DecimalField(max_digits = 19, decimal_places = 5, default = Decimal('0.000'))
    asignacion_presupuestal = models.ForeignKey('base.AsignacionPresupuestal')


class Resultado(models.Model):
    pertenece_a = models.OneToOneField(Actividad)
    t1 = models.FloatField(default=0)
    t2 = models.FloatField(default=0)
    t3 = models.FloatField(default=0)
    t4 = models.FloatField(default=0)
    t5 = models.FloatField(default=0)
    t6 = models.FloatField(default=0)
    t7 = models.FloatField(default=0)
    t8 = models.FloatField(default=0)
    t9 = models.FloatField(default=0)
    t10 = models.FloatField(default=0)
    t11 = models.FloatField(default=0)
    t12 = models.FloatField(default=0)
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
    total = models.FloatField(default=0)
    distribucion_presupuestal = models.DecimalField(max_digits = 19, decimal_places = 5, default = Decimal('0.000'))
