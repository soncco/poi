# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from decimal import Decimal
from django.contrib.auth.models import User

#@python_2_unicode_compatible
class Plan(models.Model):
    TIPOS = (
        ('2', 'Mensual'),
    )
    numero = models.CharField(max_length=100, default='')
    unidad_organica = models.ForeignKey('base.UnidadOrganica', null=True)
    area_ejecutora = models.ForeignKey('base.Unidad', null=True,blank=True)
    proyecto = models.CharField(max_length=255, null=True,blank=True)
    responsable = models.CharField(max_length=255)
    periodo = models.CharField(choices=TIPOS, default='2', max_length=1)
    presupuesto = models.DecimalField(max_digits = 19, decimal_places = 5, default = Decimal('0.000'))
    creado_por = models.ForeignKey(User, default=1)
    aprobado = models.BooleanField(default=False)
    anio = models.ForeignKey('Anio')
    act = models.CharField(max_length=255, blank=True, null=True)

class Actividad(models.Model):
    TIPOS = (
        ('1', 'Porcentual'),
        ('2', u'Numérico'),
    )
    accion = models.ForeignKey('Accion')
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

@python_2_unicode_compatible
class Anio(models.Model):
    nombre = models.IntegerField()
    activo = models.BooleanField(default=False)

    class Meta:
        verbose_name = (u'Año')
        verbose_name_plural = (u'Años')

    def __str__(self):
        return str(self.nombre)

@python_2_unicode_compatible
class Objetivo(models.Model):
    etiqueta = models.CharField(max_length=20)
    descripcion = models.CharField(max_length=255)
    anio = models.ForeignKey('Anio')

    def __str__(self):
        return '(%s) %s' % (self.anio, self.etiqueta)

    @property
    def completo(self):
        return '%s - %s' % (self.etiqueta, self.descripcion)

@python_2_unicode_compatible
class Accion(models.Model):
    etiqueta = models.CharField(max_length=20)
    descripcion = models.CharField(max_length=255)
    objetivo = models.ForeignKey('Objetivo')
    organicas = models.ManyToManyField('base.UnidadOrganica', blank=True)
    unidades = models.ManyToManyField('base.Unidad', blank=True)

    class Meta:
        verbose_name = (u'Acción')
        verbose_name_plural = ('Acciones')

    def __str__(self):
        return '%s %s' % (self.objetivo, self.etiqueta)

    @property
    def completo(self):
        return '%s - %s' % (self.etiqueta, self.descripcion)
