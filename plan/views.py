# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse

from .models import Plan


from .forms import PlanForm, ActividadForm, ActividadFormSet
from .utils import crear_enlace

from base.models import AsignacionPresupuestal

from collections import OrderedDict
import json, datetime


def plan(request):
    if request.method == 'POST':
        form = PlanForm(request.POST)
        detalle_form = ActividadFormSet(request.POST)

        if form.is_valid() and detalle_form.is_valid():
            plan = form.save(commit=False)
            plan.save()
            detalle_form.instance = plan
            detalle_form.save()
            messages.success(request, 'Se ha creado un plan.')
            return HttpResponseRedirect('%s%s%s' % (reverse('plan:planes'), '?imprimir=', plan.pk))

        else:
            print form.errors
            print detalle_form.errors

    form = PlanForm()
    detalle_form = ActividadFormSet()
    asignaciones = AsignacionPresupuestal.objects.all().order_by('rubro')
    context = {'form': form, 'detalle_form': detalle_form, 'asignaciones': asignaciones}
    return render(request, 'plan/nuevo-plan.html', context)


def planes(request):
    return render(request, 'plan/lista.html')


def planes_json(request):
    filters = []
    cols = []
    for k in request.GET:
        if 'filter[' in k:
            filters.append(k)
        if 'column[' in k:
            cols.append(k)

    size = int(request.GET.get('size'))
    page = int(request.GET.get('page'))

    limit = page * size
    offset = limit + size

    data = {
        'headers': [
            u'Unidad Orgánica', 'Unidad Ejecutora', 'Creado por', 'Acciones'
        ],
    }

    planes = Plan.objects.all().order_by('-pk')

    if 'filter[0]' in filters:
        planes = planes.filter(unidad_organica__nombre__icontains = request.GET.get('filter[0]'))

    if 'filter[1]' in filters:
        planes = planes.filter(area_ejecutora__nombre__icontains = request.GET.get('filter[1]'))

    if 'filter[2]' in filters:
        planes = planes.filter(creado__por__username__icontains = request.GET.get('filter[2]'))



    if 'column[0]' in cols:
        signo = '' if request.GET.get('column[0]') == '0' else '-'
        planes = planes.order_by('%sunidad_organica' % signo)

    if 'column[1]' in cols:
        signo = '' if request.GET.get('column[1]') == '0' else '-'
        planes = planes.order_by('%sarea_ejecutora' % signo)

    if 'column[2]' in cols:
        signo = '' if request.GET.get('column[2]') == '0' else '-'
        planes = planes.order_by('%screado_por' % signo)

    total_rows = planes.count()

    planes = planes[limit:offset]

    rows = []
    for plan in planes:

        links = crear_enlace(reverse('plan:ver_plan', args=[plan.pk]), 'warning', 'Ver o Editar', 'edit')

        obj = OrderedDict({
            '0': plan.unidad_organica.nombre,
            '1': plan.area_ejecutora.nombre,
            '2': plan.creado_por.username,
            '3': links,
        })
        rows.append(obj)

    data['rows'] = rows
    data['total_rows'] = total_rows

    return HttpResponse(json.dumps(data), content_type = "application/json")

def ver_plan(request, id):
    plan = Plan.objects.get(pk = id)
    form = PlanForm(instance = plan)
    detalle_form = ActividadFormSet()
    asignaciones = AsignacionPresupuestal.objects.all().order_by('rubro')
    context = {'form': form, 'detalle_form': detalle_form, 'asignaciones': asignaciones, 'plan': plan}
    return render(request, 'plan/ver-plan.html', context)

