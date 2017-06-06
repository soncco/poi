# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from models import *


class UnidadAdmin(admin.ModelAdmin):
  list_display = ('nombre', 'pertenece_a',)
  search_fields = ['nombre',]
  list_filter = ('pertenece_a',)

class UnidadOrganicaAdmin(admin.ModelAdmin):
  list_display = ('nombre', 'especial',)
  search_fields = ['nombre',]
  list_filter = ('especial',)

admin.site.register(Unidad, UnidadAdmin)
admin.site.register(UnidadOrganica, UnidadOrganicaAdmin)
admin.site.register(AsignacionPresupuestal)
