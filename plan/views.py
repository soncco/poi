# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q

from .models import Plan, Resultado


from .forms import PlanForm, ActividadForm, ActividadFormSet, ResultadoForm
from .utils import crear_enlace, grupo_responsable, grupo_administrador, grupo_logistico, solo_responsable, crear_resultado
from .utils import numero_plan, verificar_numero
from .mail import notificar_plan

from base.models import Unidad, AsignacionPresupuestal, UnidadOrganica

from collections import OrderedDict
import json, datetime

@login_required
def pre_plan(request):
    unidades = UnidadOrganica.objects.all()
    context = {'unidades': unidades}
    return render(request, 'plan/pre-plan.html', context)


@login_required
def plan(request):
    if request.method == 'POST':
        form = PlanForm(request.POST)
        detalle_form = ActividadFormSet(request.POST)

        if form.is_valid() and detalle_form.is_valid():
            plan = form.save(commit=False)
            plan.numero = numero_plan(plan)

            area_ejecutora = request.POST.get('area_ejecutora')
            if area_ejecutora is not None:
                area = Unidad.objects.get(pk = request.POST.get('area_ejecutora'))
                plan.area_ejecutora = area

            proyecto = request.POST.get('proyecto')
            if proyecto is not None:
                plan.proyecto = proyecto

            plan.save()
            verificar_numero(plan, request)
            detalle_form.instance = plan
            detalle_form.save()

            for actividad in plan.actividad_set.all():
                crear_resultado(actividad)

            if(request.POST.get('pre') == 'no'):
                messages.success(request, 'Se ha creado un plan.')
                #notificar_plan(plan)
                return HttpResponseRedirect('%s%s%s' % (reverse('plan:planes'), '?imprimir=', plan.pk))
            else:
                messages.success(request, 'Se ha pre-guardado el plan')
                return HttpResponseRedirect(reverse('plan:ver_plan', args=[plan.pk]))

        else:
            print form.errors
            print detalle_form.errors

    organica = request.GET.get('unidad')
    if organica is None:
        return HttpResponseRedirect(reverse('plan:pre_plan'))
    else:
        organica = UnidadOrganica.objects.get(pk = organica)

    ejecutora = request.GET.get('ejecutora')
    if ejecutora != '':
        ejecutora = Unidad.objects.get(pk = ejecutora)
    else:
        ejecutora = None

    myself = request.GET.get('myself')


    form = PlanForm()
    detalle_form = ActividadFormSet()
    asignaciones = AsignacionPresupuestal.objects.all().order_by('rubro')
    unidades = Unidad.objects.filter(pertenece_a = organica).order_by('nombre')
    context = {'form': form, 'detalle_form': detalle_form, 'asignaciones': asignaciones, 'unidades': unidades, 'organica': organica, 'ejecutora': ejecutora, 'myself': myself}
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
            u'Número', u'Año', u'Unidad Orgánica', 'Unidad Ejecutora o Proyecto', 'Responsable', 'Estado', 'Acciones'
        ],
    }

    if solo_responsable(request.user):
        planes = Plan.objects.filter(creado_por = request.user).order_by('-pk')
    else:
        planes = Plan.objects.all().order_by('-pk')

    if 'filter[0]' in filters:
        planes = planes.filter(numero = request.GET.get('filter[0]'))

    if 'filter[1]' in filters:
        planes = planes.filter(anio = request.GET.get('filter[1]'))

    if 'filter[2]' in filters:
        planes = planes.filter(unidad_organica__nombre__icontains = request.GET.get('filter[2]'))

    if 'filter[3]' in filters:
        f1 = Q(area_ejecutora__nombre__icontains = request.GET.get('filter[3]'))
        f2 = Q(proyecto__icontains = request.GET.get('filter[3]'))
        planes = planes.filter(f1 | f2)

    if 'filter[4]' in filters:
        planes = planes.filter(responsable__icontains = request.GET.get('filter[4]'))

    if 'filter[5]' in filters:
        estado = True if request.GET.get('filter[5]') == 'Aprobado' else False
        planes = planes.filter(aprobado = estado)


    if 'column[0]' in cols:
        signo = '' if request.GET.get('column[0]') == '0' else '-'
        planes = planes.order_by('%snumero' % signo)

    if 'column[1]' in cols:
        signo = '' if request.GET.get('column[1]') == '0' else '-'
        planes = planes.order_by('%sanio' % signo)

    if 'column[2]' in cols:
        signo = '' if request.GET.get('column[2]') == '0' else '-'
        planes = planes.order_by('%sunidad_organica' % signo)

    if 'column[3]' in cols:
        signo = '' if request.GET.get('column[3]') == '0' else '-'
        planes = planes.order_by('%sarea_ejecutora' % signo)

    if 'column[4]' in cols:
        signo = '' if request.GET.get('column[4]') == '0' else '-'
        planes = planes.order_by('%sresponsable' % signo)

    if 'column[5]' in cols:
        signo = '' if request.GET.get('column[5]') == '0' else '-'
        planes = planes.order_by('%saprobado' % signo)

    total_rows = planes.count()

    planes = planes[limit:offset]

    rows = []
    for plan in planes:

        if not plan.aprobado:
            links = crear_enlace(reverse('plan:ver_plan', args=[plan.pk]), 'warning', 'Ver o Editar', 'edit')
        else:
            links = crear_enlace(reverse('plan:ver_plan', args=[plan.pk]), 'primary', 'Ver o evaluar', 'eye')
        links += crear_enlace(reverse('plan:actividades', args=[plan.pk]), 'default', 'Crear cuadro de necesidades', 'table')
        links += crear_enlace(reverse('reporte:imprimir_plan', args=[plan.pk]), 'info print', 'Imprimir', 'print')
        links += crear_enlace('%s?pk=%s&amp;tipo=single' % (reverse('reporte:reporte_dependencia_excel',), plan.pk), 'success', 'Exportar a Excel', 'file-excel-o')
        if not plan.aprobado:
            links += crear_enlace(reverse('plan:borrar_plan', args=[plan.pk]), 'danger', 'Borrar', 'times')

        if plan.area_ejecutora is None:
            organica = plan.unidad_organica.nombre
            if plan.proyecto is not None:
                proyecto = plan.proyecto
            else:
                proyecto = organica
        else:
            organica = plan.area_ejecutora.pertenece_a.nombre
            proyecto = plan.area_ejecutora.nombre

        obj = OrderedDict({
            '0': plan.numero,
            '1': plan.anio,
            '2': organica,
            '3': proyecto,
            '4': plan.responsable,
            '5': "Aprobado" if plan.aprobado else "Sin aprobar",
            '6': links,
        })
        rows.append(obj)

    data['rows'] = rows
    data['total_rows'] = total_rows

    return HttpResponse(json.dumps(data), content_type = "application/json")

@login_required
def ver_plan(request, id):
    plan = Plan.objects.get(id__exact = id)
    if solo_responsable(request.user):
        if request.user != plan.creado_por:
            messages.warning(request, 'No puedes ver planes que no te pertenecen.')
            return HttpResponseRedirect(reverse('plan:planes'))

    if request.method == 'POST':
        form  = PlanForm(request.POST, instance = plan)

        if form.is_valid():
            plan = form.save(commit=False)
            plan.numero = request.POST.get('numero')

            area_ejecutora = request.POST.get('area_ejecutora')
            if area_ejecutora is not None:
                area = Unidad.objects.get(pk = request.POST.get('area_ejecutora'))
                plan.area_ejecutora = area

            proyecto = request.POST.get('proyecto')
            if proyecto is not None:
                plan.proyecto = proyecto

            detalle_form = ActividadFormSet(request.POST, request.FILES, instance = plan)
            if detalle_form.is_valid():
                plan.save()
                verificar_numero(plan, request)
                detalle_form.save()

                for actividad in plan.actividad_set.all():
                    crear_resultado(actividad)

                if(request.POST.get('pre') == 'no'):
                    messages.success(request, 'Se ha modificado el Plan.')
                    return HttpResponseRedirect('%s%s%s' % (reverse('plan:planes'), '?imprimir=', plan.pk))
                else:
                    messages.success(request, 'Se ha pre-guardado el plan')
                    return HttpResponseRedirect(reverse('plan:ver_plan', args=[plan.pk]))

            else:
                print detalle_form.errors
        else:
            print form.errors


    form = PlanForm(instance = plan)
    detalle_form = ActividadFormSet(instance=plan)
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

@login_required
def actividades(request, id):
    plan = Plan.objects.get(pk = id)
    context = {'plan': plan}
    return render(request, 'plan/actividades.html', context)


# Informes
@login_required
@user_passes_test(grupo_administrador)
def informe_dependencia(request):
    unidades = Unidad.objects.all()
    context = {'unidades': unidades}
    return render(request, 'plan/informe-dependencia.html', context)

@login_required
@user_passes_test(grupo_administrador)
def informe_organica(request):
    unidades = UnidadOrganica.objects.all()
    context = {'unidades': unidades}
    return render(request, 'plan/informe-organica.html', context)

@login_required
@user_passes_test(grupo_administrador)
def informe_institucion(request):
    context = {}
    return render(request, 'plan/informe-institucion.html', context)

@login_required
@user_passes_test(grupo_administrador)
def informe_resumen(request):
    context = {}
    return render(request, 'plan/informe-resumen.html', context)

