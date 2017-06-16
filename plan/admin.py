# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from models import *


class PlanAdmin(admin.ModelAdmin):
  list_display = ('numero', 'unidad_organica', 'responsable', 'anio', 'aprobado')
  search_fields = ['numero', 'responsable']
  list_filter = ('anio', 'unidad_organica', 'periodo', 'aprobado',)

admin.site.register(Plan, PlanAdmin)
