# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, user_passes_test

from .models import Plan, Resultado


from .forms import PlanForm, ActividadForm, ActividadFormSet, ResultadoForm
from .utils import crear_enlace, grupo_responsable, grupo_administrador, grupo_logistico, solo_responsable, crear_resultado

from base.models import AsignacionPresupuestal

from collections import OrderedDict
import json, datetime

@login_required
def plan(request):
    if request.method == 'POST':
        form = PlanForm(request.POST)
        detalle_form = ActividadFormSet(request.POST)

        if form.is_valid() and detalle_form.is_valid():
            plan = form.save(commit=False)
            plan.save()
            detalle_form.instance = plan
            detalle_form.save()

            for actividad in plan.actividad_set.all():
                crear_resultado(actividad)
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

@login_required
def planes(request):
    return render(request, 'plan/lista.html')

@login_required
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
            u'Unidad Orgánica', 'Unidad Ejecutora', 'Responsable', 'Estado', 'Acciones'
        ],
    }

    if solo_responsable(request.user):
        planes = Plan.objects.filter(creado_por = request.user).order_by('-pk')
    else:
        planes = Plan.objects.all().order_by('-pk')

    if 'filter[0]' in filters:
        planes = planes.filter(unidad_organica__nombre__icontains = request.GET.get('filter[0]'))

    if 'filter[1]' in filters:
        planes = planes.filter(area_ejecutora__nombre__icontains = request.GET.get('filter[1]'))

    if 'filter[2]' in filters:
        planes = planes.filter(responsable__icontains = request.GET.get('filter[2]'))

    if 'filter[3]' in filters:
        estado = True if request.GET.get('filter[3]') == 'Aprobado' else False
        planes = planes.filter(aprobado = estado)



    if 'column[0]' in cols:
        signo = '' if request.GET.get('column[0]') == '0' else '-'
        planes = planes.order_by('%sunidad_organica' % signo)

    if 'column[1]' in cols:
        signo = '' if request.GET.get('column[1]') == '0' else '-'
        planes = planes.order_by('%sarea_ejecutora' % signo)

    if 'column[2]' in cols:
        signo = '' if request.GET.get('column[2]') == '0' else '-'
        planes = planes.order_by('%sresponsable' % signo)

    if 'column[2]' in cols:
        signo = '' if request.GET.get('column[3]') == '0' else '-'
        planes = planes.order_by('%saprobado' % signo)

    total_rows = planes.count()

    planes = planes[limit:offset]

    rows = []
    for plan in planes:

        if not plan.aprobado:
            links = crear_enlace(reverse('plan:ver_plan', args=[plan.pk]), 'warning', 'Ver o Editar', 'edit')
        else:
            links = crear_enlace(reverse('plan:ver_plan', args=[plan.pk]), 'primary', 'Ver o evaluar', 'eye')
        links += crear_enlace(reverse('reporte:imprimir_plan', args=[plan.pk]), 'info print', 'Imprimir', 'print')
        links += crear_enlace(reverse('plan:borrar_plan', args=[plan.pk]), 'danger', 'Borrar', 'times')

        obj = OrderedDict({
            '0': plan.unidad_organica.nombre,
            '1': plan.area_ejecutora.nombre,
            '2': plan.responsable,
            '3': "Aprobado" if plan.aprobado else "Sin aprobar",
            '4': links,
        })
        rows.append(obj)

    data['rows'] = rows
    data['total_rows'] = total_rows

    return HttpResponse(json.dumps(data), content_type = "application/json")

@login_required
def ver_plan(request, id):
    plan = Plan.objects.get(pk = id)
    if solo_responsable(request.user):
        if request.user != plan.creado_por:
            messages.warning(request, 'No puedes ver planes que no te pertenecen.')
            return HttpResponseRedirect(reverse('plan:planes'))

    if request.method == 'POST':
        form  = PlanForm(request.POST, instance = plan)

        if form.is_valid():
            plan = form.save(commit=False)
            detalle_form = ActividadFormSet(request.POST, instance = plan)
            if detalle_form.is_valid():
                plan.save()
                for actividad in plan.actividad_set.all():
                    actividad.delete()
                detalle_form.save()

                for actividad in plan.actividad_set.all():
                    crear_resultado(actividad)

                messages.success(request, 'Se ha modificado el Plan.')
                return HttpResponseRedirect(reverse('plan:planes'))

            else:
                print detalle_form.errors
        else:
            print form.errors


    form = PlanForm(instance = plan)
    detalle_form = ActividadFormSet()
    asignaciones = AsignacionPresupuestal.objects.all().order_by('rubro')
    context = {'form': form, 'detalle_form': detalle_form, 'asignaciones': asignaciones, 'plan': plan}

    if not plan.aprobado:
        return render(request, 'plan/editar-plan.html', context)
    else:
        return render(request, 'plan/ver-plan.html', context)


@login_required
def borrar_plan(request, id):
    plan = Plan.objects.get(pk = id)
    if solo_responsable(request.user):
        if plan.creado_por != request.user:
            messages.error(request, u'¿Qué tratas de hacer? No puedes tocar otros planes.')
    else:
        plan.delete()
        messages.success(request, u'Se ha borrado el plan.')

    return HttpResponseRedirect(reverse('plan:planes'))


@login_required
@user_passes_test(grupo_administrador)
def aprobar_plan(request, id):
    plan = Plan.objects.get(pk = id)
    plan.aprobado = False
    plan.save()
    messages.success(request, u'Se ha quitado la aprobación el plan.')    

    return HttpResponseRedirect(reverse('plan:planes'))

@login_required
@user_passes_test(grupo_administrador)
def guardar_actividad(request):
    pk = request.POST.get('pk')
    resultado = Resultado.objects.get(pk = pk)
    form  = ResultadoForm(request.POST, instance = resultado)
    form.save()
    return HttpResponse(pk)
