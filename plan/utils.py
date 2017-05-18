# -*- coding: utf-8 -*-
from models import Resultado
def crear_enlace(href, clase, titulo, icono):
    return '<a href="%s" class="btn btn-%s btn-xs" title="%s"><i class="fa fa-%s"></i></a> ' % (href, clase, titulo, icono)

def grupo_responsable(user):
    return user.groups.filter(name='Responsable').exists()

def grupo_logistico(user):
    return user.groups.filter(name='Logística').exists()

def grupo_administrador(user):
    return user.groups.filter(name='Administrador').exists()

def solo_responsable(user):
    permisos = grupo_responsable(user) and not grupo_logistico(user) and not grupo_administrador(user)
    return permisos

def crear_resultado(actividad):
    resultado = Resultado(pertenece_a = actividad)
    resultado.save()
