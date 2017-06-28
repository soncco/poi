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

admin.site.register(Plan, PlanAdmin)

