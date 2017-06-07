# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from models import *


class ProductoAdmin(admin.ModelAdmin):
  list_display = ('descripcion',)
  search_fields = ['descripcion',]

admin.site.register(Producto, ProductoAdmin)