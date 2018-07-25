# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from models import *

class ActividadInline(admin.TabularInline):
    model = Actividad
    # raw_id_fields = ('producto',)



class PlanAdmin(admin.ModelAdmin):
  inlines = [ActividadInline]
  list_display = ('numero', 'unidad_organica', 'responsable', 'anio', 'aprobado')
  search_fields = ['numero', 'responsable']
  list_filter = ('anio', 'unidad_organica', 'periodo', 'aprobado',)

class AnioAdmin(admin.ModelAdmin):
  list_display = ('nombre', 'activo',)
  list_filter = ('activo',)

class ObjetivoAdmin(admin.ModelAdmin):
  list_display = ('etiqueta', 'descripcion', 'anio',)
  search_fields = ['etiqueta', 'descripcion']
  list_filter = ('anio',)

class AccionAdmin(admin.ModelAdmin):
  list_display = ('etiqueta', 'objetivo',)
  search_fields = ['etiqueta', 'descripcion']
  list_filter = ('objetivo__anio', 'objetivo__etiqueta')

admin.site.register(Plan, PlanAdmin)
admin.site.register(Anio, AnioAdmin)

admin.site.register(Objetivo, ObjetivoAdmin)
admin.site.register(Accion, AccionAdmin)
