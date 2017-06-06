# -*- coding: utf-8 -*-

from django import template

register = template.Library()

@register.assignment_tag
def tag_mi_grupo(grupo, usuario):
  return grupo in usuario.groups.all()
