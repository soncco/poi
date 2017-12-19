# -*- coding: utf-8 -*-
from models import Resultado, Plan
from django.contrib import messages

import re

def crear_enlace(href, clase, titulo, icono):
    return '<a href="%s" class="btn btn-%s btn-xs" title="%s"><i class="fa fa-%s"></i></a> ' % (href, clase, titulo, icono)

def grupo_responsable(user):
    return user.groups.filter(name='Responsable').exists()

def grupo_logistico(user):
    return user.groups.filter(name='Logistico').exists()

def grupo_administrador(user):
    return user.groups.filter(name='Administrador').exists()

def grupo_jefe(user):
    return user.groups.filter(name='Jefe').exists()

def solo_responsable(user):
    permisos = grupo_responsable(user) and not grupo_logistico(user) and not grupo_administrador(user) and not grupo_jefe(user)
    return permisos

def crear_resultado(actividad):
    try:
        resultado = Resultado.objects.get(pertenece_a = actividad)
    except:
        resultado = Resultado(pertenece_a = actividad)
        resultado.save()

def numero_plan(plan):
    ultimo = Plan.objects.filter(area_ejecutora = plan.area_ejecutora, anio = plan.anio).last()
    if ultimo is not None:
        list_numero = re.findall(r'\d+', ultimo.numero)
        if len(list_numero) > 0:
            numero = int(list_numero[0])
            return numero + 1
        else:
            numero = Plan.objects.filter(area_ejecutora = plan.area_ejecutora, anio = plan.anio).count() + 1
            return numero
    else:
        numero = Plan.objects.filter(area_ejecutora = plan.area_ejecutora, anio = plan.anio).count() + 1
        return numero

def verificar_numero(plan, request):

    total = Plan.objects.filter(area_ejecutora = plan.area_ejecutora, numero = plan.numero, anio = plan.anio).count()
    if total > 1:
        plan.numero = int(plan.numero) + 1
        plan.save()
        verificar_numero(plan, request)
        messages.warning(request, 'El número de Plan ya existía, el sistema automáticamente asignó el número siguiente.')
    elif total == 0:
        plan.numero = Plan.objects.filter(area_ejecutora = plan.area_ejecutora, anio = plan.anio).count() + 1
        plan.save()
        verificar_numero(plan, request)
    elif total == 1:
        if(plan.numero == '0'):
            plan.numero = Plan.objects.filter(area_ejecutora = plan.area_ejecutora, anio = plan.anio).count()
            plan.save()
