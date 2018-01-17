# -*- coding: utf-8 -*-
from io import BytesIO

from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.contrib import messages
from django.core.urlresolvers import reverse

from plan.models import Plan
from printable import ImpresionPlan, ImpresionCuadro
from plan.utils import solo_responsable, grupo_administrador, grupo_logistico

from base.models import Unidad, UnidadOrganica

from cuadro.models import Cuadro, CuadroDetalle, Producto

from utils import traer_suma

from xlsxwriter.workbook import Workbook
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

from datetime import date
import datetime


@login_required
def imprimir_plan(request, id):
    response = HttpResponse(content_type='application/pdf')
    
    buffer = BytesIO()
    try:
        plan = get_object_or_404(Plan, pk = id)
    except:
        raise Http404

    if solo_responsable(request.user):
        if request.user != plan.creado_por:
            messages.warning(request, 'No puedes ver planes que no te pertenecen.')
            return HttpResponseRedirect(reverse('plan:planes'))

    report = ImpresionPlan(buffer, 'A4')
    pdf = report.print_plan(plan)

    response.write(pdf)
    return response


@login_required
def reporte_dependencia_excel(request):
    unidad = request.POST.get('unidad')
    anio = request.POST.get('anio')
    tipo = request.POST.get('tipo')

    if tipo == 'dependencia':
        if not solo_responsable(request.user):
            oficina = Unidad.objects.get(pk = unidad)
            planes = Plan.objects.filter(area_ejecutora = oficina, anio = anio)
            nombre = oficina.nombre
            titulo_hoja = 'Trabajos por Dependencia'
        else:
            messages.warning(request, 'El tipo de reporte no es correcto.')
            return HttpResponseRedirect(reverse('plan:planes'))
    elif tipo == 'organica':
        if not solo_responsable(request.user):
            unidad_organica = UnidadOrganica.objects.get(pk = unidad)
            planes = Plan.objects.filter(area_ejecutora__pertenece_a = unidad_organica, anio = anio)
            nombre = unidad_organica.nombre
            titulo_hoja = u'Trabajos por Unidad Orgánica'
        else:
            messages.warning(request, 'El tipo de reporte no es correcto.')
            return HttpResponseRedirect(reverse('plan:planes'))
    elif tipo == 'institucion':
        if not solo_responsable(request.user):
            planes = Plan.objects.filter(anio = anio)
            nombre = 'Municipalidad'
            titulo_hoja = u'Trabajos por Institución'
        else:
            messages.warning(request, 'El tipo de reporte no es correcto.')
            return HttpResponseRedirect(reverse('plan:planes'))
    else:
        pk = request.GET.get('pk')
        tipo = request.GET.get('tipo')
        if tipo == 'single':
            planes = Plan.objects.filter(pk = pk)
            nombre = 'simple-' + str(planes[0].numero)
            titulo_hoja = 'Plan operativo'
        else:
            messages.warning(request, 'El tipo de reporte no es correcto.')
            return HttpResponseRedirect(reverse('plan:planes'))
    
    output = StringIO.StringIO()

    book = Workbook(output)
    sheet = book.add_worksheet(nombre[:30])
    sheet.set_landscape()
    sheet.set_paper(9)

    titulo = book.add_format({
        'bold': 1,
        'align': 'center'
    })

    negrita = book.add_format({'bold': 1})
    fecha = book.add_format({'num_format': 'dd/mm/yy'})
    dinero = book.add_format({'num_format': '0.00'})
    dinero_item = book.add_format({'num_format': '0.00', 'fg_color': '#BADDF5'})
    item = book.add_format({'fg_color': '#BADDF5'})

    wrap = book.add_format({'text_wrap': True})

    negrita_borde = book.add_format({'bold': 1, 'border': 1, 'fg_color': '#BADDF5', 'valign': 'vcenter', 'text_wrap': True, 'align': 'center'})
    borde = book.add_format({'border': 1})
    borde_numero = book.add_format({'border': 1, 'num_format': '0.00'})
    borde_fecha = book.add_format({'num_format': 'dd/mm/yy', 'border': 1})

    hasta = 'Y'

    sheet.merge_range('A1:%s1' % hasta, titulo_hoja, titulo)
    sheet.merge_range('B2:%s2' % hasta, 'ACCIONES CENTRALES', titulo)

    k = 4

    for plan in planes:
        sheet.write('A%s' % str(k-1), u'Número de Plan', negrita)
        sheet.write('B%s' % str(k-1), plan.numero)

        sheet.write('A%s' % k, u'Unidad Orgánica', negrita)
        sheet.merge_range('B%s:H%s' % (k, k), plan.unidad_organica.nombre)
        
        sheet.write('I%s' % k, u'Presupuesto S/', negrita)
        sheet.merge_range('J%s:M%s' % (k, k), plan.presupuesto, dinero)
        k += 1

        if plan.area_ejecutora is not None:
            sheet.write('A%s' % k, u'Área Ejecutora', negrita)
            sheet.merge_range('B%s:H%s' % (k, k), plan.area_ejecutora.nombre)
        else:
            if plan.proyecto is not None:
                sheet.write('A%s' % k, u'Proyecto', negrita)
                sheet.merge_range('B%s:H%s' % (k, k), plan.proyecto)
            else:
                sheet.write('A%s' % k, u'Área Ejecutora', negrita)
                sheet.merge_range('B%s:H%s' % (k, k), plan.unidad_organica.nombre)
        
        sheet.write('I%s' % k, u'Año', negrita)
        sheet.merge_range('J%s:M%s' % (k, k), plan.anio)
        k += 1

        if plan.area_ejecutora is not None:
            sheet.write('A%s' % k, u'Responsable', negrita)
        else:
            if plan.proyecto is not None:
                sheet.write('A%s' % k, u'Residente', negrita)
            else:
                sheet.write('A%s' % k, u'Responsable', negrita)
        sheet.merge_range('B%s:H%s' % (k, k), plan.responsable)
        k += 1

        sheet.write('A%s' % k, u'Acción Central', negrita)
        sheet.merge_range('B%s:%s%s' % (k, hasta, k), plan.accion_central, wrap)
        k += 1

        sheet.write('A%s' % k, u'Objetivo General', negrita)
        sheet.merge_range('B%s:%s%s' % (k, hasta, k), plan.objetivo_general_institucional, wrap)
        k += 1

        sheet.write('A%s' % k, u'Objetivo Específico', negrita)
        sheet.merge_range('B%s:%s%s' % (k, hasta, k), plan.objetivo_especifico_institucional, wrap)
        k += 1

        if plan.unidad_organica.actividades == True:
            if plan.area_ejecutora is not None:
                sheet.write('A%s' % k, u'Actividad', negrita)
                sheet.merge_range('B%s:%s%s' % (k, hasta, k), plan.act if plan.act is not None else '', wrap)
                k += 1

        inicio = k + 4

        if plan.unidad_organica.actividades == True:
            if plan.area_ejecutora is not None:
                sheet.merge_range('A%s:A%s' % (k, k+3), u'Tarea', negrita_borde)
            else:
                sheet.merge_range('A%s:A%s' % (k, k+3), u'Actividad', negrita_borde)
        else:
            sheet.merge_range('A%s:A%s' % (k, k+3), u'Actividad', negrita_borde)

        sheet.merge_range('B%s:B%s' % (k, k+3), u'Unidad de medida', negrita_borde)
        sheet.merge_range('C%s:C%s' % (k, k+3), u'Peso', negrita_borde)
        sheet.merge_range('D%s:AA%s' % (k, k), u'Ejecución', negrita_borde)
        sheet.merge_range('D%s:AA%s' % (k+1, k+1), u'Programado vs Ejecutado', negrita_borde)
        sheet.merge_range('AB%s:AB%s' % (k, k+3), u'Programado', negrita_borde)
        sheet.merge_range('AC%s:AC%s' % (k, k+3), u'Ejecutado', negrita_borde)
        sheet.merge_range('AD%s:AD%s' % (k, k+3), u'Grado cumplimiento', negrita_borde)
        sheet.merge_range('AE%s:AE%s' % (k, k+3), u'Alerta de gestión', negrita_borde)
        sheet.merge_range('AF%s:AF%s' % (k, k+3), u'Distribución presupuestal', negrita_borde)
        sheet.merge_range('AG%s:AG%s' % (k, k+3), u'Fuente', negrita_borde)
        sheet.merge_range('AH%s:AH%s' % (k, k+3), u'Fecha Término', negrita_borde)
        k += 4
        q = k-2
        c = k-1


        if plan.get_periodo_display() == 'Mensual':
            sheet.merge_range('D%s:E%s' % (q, q), 'Ene', negrita_borde)
            sheet.merge_range('F%s:G%s' % (q, q), 'Feb', negrita_borde)
            sheet.merge_range('H%s:I%s' % (q, q), 'Mar', negrita_borde)
            sheet.merge_range('J%s:K%s' % (q, q), 'Abr', negrita_borde)
            sheet.merge_range('L%s:M%s' % (q, q), 'May', negrita_borde)
            sheet.merge_range('N%s:O%s' % (q, q), 'Jun', negrita_borde)
            sheet.merge_range('P%s:Q%s' % (q, q), 'Jul', negrita_borde)
            sheet.merge_range('R%s:S%s' % (q, q), 'Ago', negrita_borde)
            sheet.merge_range('T%s:U%s' % (q, q), 'Set', negrita_borde)
            sheet.merge_range('V%s:W%s' % (q, q), 'Oct', negrita_borde)
            sheet.merge_range('X%s:Y%s' % (q, q), 'Nov', negrita_borde)
            sheet.merge_range('Y%s:AA%s' % (q, q), 'Dic', negrita_borde)

            sheet.write('D%s' % c, u'Prog', negrita_borde)
            sheet.write('E%s' % c, u'Eje', negrita_borde)
            sheet.write('F%s' % c, u'Prog', negrita_borde)
            sheet.write('G%s' % c, u'Eje', negrita_borde)
            sheet.write('H%s' % c, u'Prog', negrita_borde)
            sheet.write('I%s' % c, u'Eje', negrita_borde)
            sheet.write('J%s' % c, u'Prog', negrita_borde)
            sheet.write('K%s' % c, u'Eje', negrita_borde)
            sheet.write('L%s' % c, u'Prog', negrita_borde)
            sheet.write('M%s' % c, u'Eje', negrita_borde)
            sheet.write('N%s' % c, u'Prog', negrita_borde)
            sheet.write('O%s' % c, u'Eje', negrita_borde)
            sheet.write('P%s' % c, u'Prog', negrita_borde)
            sheet.write('Q%s' % c, u'Eje', negrita_borde)
            sheet.write('R%s' % c, u'Prog', negrita_borde)
            sheet.write('S%s' % c, u'Eje', negrita_borde)
            sheet.write('T%s' % c, u'Prog', negrita_borde)
            sheet.write('U%s' % c, u'Eje', negrita_borde)
            sheet.write('V%s' % c, u'Prog', negrita_borde)
            sheet.write('W%s' % c, u'Eje', negrita_borde)
            sheet.write('X%s' % c, u'Prog', negrita_borde)
            sheet.write('Y%s' % c, u'Eje', negrita_borde)
            sheet.write('Z%s' % c, u'Prog', negrita_borde)
            sheet.write('AA%s' % c, u'Eje', negrita_borde)
        else: # Trimestral
            sheet.merge_range('D%s:I%s' % (q, q), 'T1', negrita_borde)
            sheet.merge_range('J%s:O%s' % (q, q), 'T2', negrita_borde)
            sheet.merge_range('P%s:U%s' % (q, q), 'T3', negrita_borde)
            sheet.merge_range('V%s:AA%s' % (q, q), 'T4', negrita_borde)

            sheet.merge_range('D%s:F%s' % (c, c), u'Prog', negrita_borde)
            sheet.merge_range('G%s:I%s' % (c, c), u'Eje', negrita_borde)
            sheet.merge_range('J%s:L%s' % (c, c), u'Prog', negrita_borde)
            sheet.merge_range('M%s:O%s' % (c, c), u'Eje', negrita_borde)
            sheet.merge_range('P%s:R%s' % (c, c), u'Prog', negrita_borde)
            sheet.merge_range('S%s:U%s' % (c, c), u'Eje', negrita_borde)
            sheet.merge_range('V%s:X%s' % (c, c), u'Prog', negrita_borde)
            sheet.merge_range('Y%s:AA%s' % (c, c), u'Eje', negrita_borde)


            
        for actividad in plan.actividad_set.all():
            sheet.merge_range('A%s:A%s' % (k, k+1), actividad.tarea_actividad, borde)
            sheet.merge_range('B%s:B%s' % (k, k+1), actividad.unidad_medida, borde)
            sheet.merge_range('C%s:C%s' % (k, k+1), actividad.peso, borde_numero)
            sheet.merge_range('AF%s:AF%s' % (k, k+1), actividad.distribucion_presupuestal, borde_numero)
            sheet.merge_range('AG%s:AG%s' % (k, k+1), actividad.asignacion_presupuestal.fuente, borde)
            sheet.merge_range('AH%s:AH%s' % (k, k+1), actividad.fecha_termino, borde_fecha)


            if plan.get_periodo_display() == 'Mensual':
                # Número.
                sheet.write('D%s' % k, actividad.t1, borde_numero)
                sheet.write('E%s' % k, actividad.resultado.t1, borde_numero)

                sheet.write('F%s' % k, actividad.t2, borde_numero)
                sheet.write('G%s' % k, actividad.resultado.t2, borde_numero)

                sheet.write('H%s' % k, actividad.t3, borde_numero)
                sheet.write('I%s' % k, actividad.resultado.t3, borde_numero)

                sheet.write('J%s' % k, actividad.t4, borde_numero)
                sheet.write('K%s' % k, actividad.resultado.t4, borde_numero)

                sheet.write('L%s' % k, actividad.t5, borde_numero)
                sheet.write('M%s' % k, actividad.resultado.t5, borde_numero)

                sheet.write('N%s' % k, actividad.t6, borde_numero)
                sheet.write('O%s' % k, actividad.resultado.t6, borde_numero)

                sheet.write('P%s' % k, actividad.t7, borde_numero)
                sheet.write('Q%s' % k, actividad.resultado.t7, borde_numero)

                sheet.write('R%s' % k, actividad.t8, borde_numero)
                sheet.write('S%s' % k, actividad.resultado.t8, borde_numero)

                sheet.write('T%s' % k, actividad.t9, borde_numero)
                sheet.write('U%s' % k, actividad.resultado.t9, borde_numero)

                sheet.write('V%s' % k, actividad.t10, borde_numero)
                sheet.write('W%s' % k, actividad.resultado.t10, borde_numero)

                sheet.write('X%s' % k, actividad.t11, borde_numero)
                sheet.write('Y%s' % k, actividad.resultado.t11, borde_numero)

                sheet.write('Z%s' % k, actividad.t12, borde_numero)
                sheet.write('AA%s' % k, actividad.resultado.t12, borde_numero)

                # Programado
                formula = '=SUM(D{0},F{0},H{0},J{0},L{0},N{0},P{0},R{0},T{0},V{0},X{0},Z{0})'.format(k)
                formula1 = '=SUM(D{0},F{0},H{0},J{0},L{0},N{0},P{0},R{0},T{0},V{0},X{0},Z{0})'.format(str(k+1))
                sheet.write_formula('AB%s' % k, formula, borde_numero)
                sheet.write_formula('AB%s' % str(k+1), formula1, borde_numero)


                # Monto.
                sheet.write('D%s' % str(k+1), actividad.p1, borde_numero)
                sheet.write('E%s' % str(k+1), actividad.resultado.p1, borde_numero)

                sheet.write('F%s' % str(k+1), actividad.p2, borde_numero)
                sheet.write('G%s' % str(k+1), actividad.resultado.p2, borde_numero)

                sheet.write('H%s' % str(k+1), actividad.p3, borde_numero)
                sheet.write('I%s' % str(k+1), actividad.resultado.p3, borde_numero)

                sheet.write('J%s' % str(k+1), actividad.p4, borde_numero)
                sheet.write('K%s' % str(k+1), actividad.resultado.p4, borde_numero)

                sheet.write('L%s' % str(k+1), actividad.p5, borde_numero)
                sheet.write('M%s' % str(k+1), actividad.resultado.p5, borde_numero)

                sheet.write('N%s' % str(k+1), actividad.p6, borde_numero)
                sheet.write('O%s' % str(k+1), actividad.resultado.p6, borde_numero)

                sheet.write('P%s' % str(k+1), actividad.p7, borde_numero)
                sheet.write('Q%s' % str(k+1), actividad.resultado.p7, borde_numero)

                sheet.write('R%s' % str(k+1), actividad.p8, borde_numero)
                sheet.write('S%s' % str(k+1), actividad.resultado.p8, borde_numero)

                sheet.write('T%s' % str(k+1), actividad.p9, borde_numero)
                sheet.write('U%s' % str(k+1), actividad.resultado.p9, borde_numero)

                sheet.write('V%s' % str(k+1), actividad.p10, borde_numero)
                sheet.write('W%s' % str(k+1), actividad.resultado.p10, borde_numero)

                sheet.write('X%s' % str(k+1), actividad.p11, borde_numero)
                sheet.write('Y%s' % str(k+1), actividad.resultado.p11, borde_numero)

                sheet.write('Z%s' % str(k+1), actividad.p12, borde_numero)
                sheet.write('AA%s' % str(k+1), actividad.resultado.p12, borde_numero)

                # Ejecutado.
                formula = '=SUM(E{0},G{0},I{0},K{0},M{0},O{0},Q{0},S{0},U{0},W{0},Y{0},AA{0})'.format(k)
                formula1 = '=SUM(E{0},G{0},I{0},K{0},M{0},O{0},Q{0},S{0},U{0},W{0},Y{0},AA{0})'.format(str(k+1))
                sheet.write_formula('AC%s' % k, formula, borde_numero)
                sheet.write_formula('AC%s' % str(k+1), formula1, borde_numero)

            else: # Trimestral
                # Número.
                sheet.merge_range('D%s:F%s' % (k, k), actividad.t1, borde_numero)
                sheet.merge_range('G%s:I%s' % (k, k), actividad.resultado.t1, borde_numero)
                sheet.merge_range('J%s:L%s' % (k, k), actividad.t2, borde_numero)
                sheet.merge_range('M%s:O%s' % (k, k), actividad.resultado.t2, borde_numero)
                sheet.merge_range('P%s:R%s' % (k, k), actividad.t3, borde_numero)
                sheet.merge_range('S%s:U%s' % (k, k), actividad.resultado.t3, borde_numero)
                sheet.merge_range('V%s:X%s' % (k, k), actividad.t4, borde_numero)
                sheet.merge_range('Y%s:AA%s' % (k, k), actividad.resultado.t4, borde_numero)

                # Programado
                formula = '=SUM(D{0},J{0},P{0},V{0})'.format(k)
                formula1 = '=SUM(D{0},J{0},P{0},V{0})'.format(str(k+1))
                sheet.write_formula('AB%s' % k, formula, borde_numero)
                sheet.write_formula('AB%s' % str(k+1), formula1, borde_numero)

                # Monto.
                sheet.merge_range('D%s:F%s' % (k+1, k+1), actividad.p1, borde_numero)
                sheet.merge_range('G%s:I%s' % (k+1, k+1), actividad.resultado.p1, borde_numero)
                sheet.merge_range('J%s:L%s' % (k+1, k+1), actividad.p2, borde_numero)
                sheet.merge_range('M%s:O%s' % (k+1, k+1), actividad.resultado.p2, borde_numero)
                sheet.merge_range('P%s:R%s' % (k+1, k+1), actividad.p3, borde_numero)
                sheet.merge_range('S%s:U%s' % (k+1, k+1), actividad.resultado.p3, borde_numero)
                sheet.merge_range('V%s:X%s' % (k+1, k+1), actividad.p4, borde_numero)
                sheet.merge_range('Y%s:AA%s' % (k+1, k+1), actividad.resultado.p4, borde_numero)

                # Ejecutado.
                formula = '=SUM(G{0},M{0},S{0},Y{0})'.format(k)
                formula1 = '=SUM(G{0},M{0},S{0},Y{0})'.format(str(k+1))
                sheet.write_formula('AC%s' % k, formula, borde_numero)
                sheet.write_formula('AC%s' % str(k+1), formula1, borde_numero)


            # Porcentaje.
            formula = '=AC{0}*100/AB{0}'.format(k)
            formula1 = '=AC{0}*100/AB{0}'.format(str(k+1))
            sheet.write_formula('AD%s' % k, formula, borde_numero)
            sheet.write_formula('AD%s' % str(k+1), formula1, borde_numero)

            # Alerta.
            formula = '=IF(AD{0}=0, "No programado", IF(AD{0}<50, "Retrasado", IF(AD{0}>=75, "Aceptable", IF(AD{0}<=100, "Adecuado"))))'.format(k)
            formula1 = '=IF(AD{0}=0, "No programado", IF(AD{0}<50, "Retrasado", IF(AD{0}>=75, "Aceptable", IF(AD{0}<=100, "Adecuado"))))'.format(str(k+1))
            sheet.write_formula('AE%s' % k, formula, borde_numero)
            sheet.write_formula('AE%s' % str(k+1), formula1, borde_numero)


            k += 2

        sheet.write('AE%s' % k, 'Total', negrita_borde)
        sheet.write_formula('AF%s' % k, '=SUM(AF%s:AF%s)' % (inicio, k-1) , borde_numero)

        # Fin loop
        k += 2



    book.close()

    output.seek(0)
    response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = "attachment; filename=reporte-%s.xlsx" % nombre

    return response

@login_required
def imprimir_cuadro(request, id):
    response = HttpResponse(content_type='application/pdf')
    
    buffer = BytesIO()
    try:
        cuadro = get_object_or_404(Cuadro, pk = id)
    except:
        raise Http404

    report = ImpresionCuadro(buffer, 'A4')
    pdf = report.print_cuadro(cuadro)

    response.write(pdf)
    return response

@login_required
def cuadro_excel(request):
    tipo = request.GET.get('tipo')

    if tipo == 'cuadro':
        pk = request.GET.get('cuadro')
        cuadro = Cuadro.objects.filter(pk = pk)
        actividad = cuadro[0].actividad
        plan = actividad.pertenece_a
        anio = actividad.pertenece_a.anio
        gerencia = actividad.pertenece_a.unidad_organica.nombre

        if plan.area_ejecutora is not None:
            titulo_area = u'Área Ejecutora:'
            nombre_area = plan.area_ejecutora.nombre
        else:
            if plan.proyecto is not None:
                titulo_area = u'Proyecto:'
                nombre_area = plan.proyecto
            else:
                titulo_area = u'Área Ejecutora:'
                nombre_area = plan.unidad_organica.nombre

        sec_func = cuadro[0].sec_func

        act_titulo = 'Actividad'
        act_nombre = actividad.tarea_actividad

    if tipo == 'plan':
        pk = request.GET.get('plan')
        plan = Plan.objects.get(pk = pk)
        anio = plan.anio
        gerencia = plan.unidad_organica.nombre

        if plan.area_ejecutora is not None:
            titulo_area = u'Área Ejecutora:'
            nombre_area = plan.area_ejecutora.nombre
        else:
            if plan.proyecto is not None:
                titulo_area = u'Proyecto:'
                nombre_area = plan.proyecto
            else:
                titulo_area = u'Área Ejecutora:'
                nombre_area = plan.unidad_organica.nombre

        sec_func = ''

        act_titulo = 'Plan Nro:'
        act_nombre = plan.numero

    if tipo == 'dependencia':
        pk = request.GET.get('unidad')
        unidad = Unidad.objects.get(pk = pk)
        anio = request.GET.get('anio')
        gerencia = unidad.pertenece_a.nombre

        titulo_area = u'Área Ejecutora:'
        nombre_area = unidad.nombre

        sec_func = ''

        act_titulo = ''
        act_nombre = ''

    if tipo == 'organica':
        pk = request.GET.get('unidad')
        unidad = UnidadOrganica.objects.get(pk = pk)
        anio = request.GET.get('anio')
        gerencia = unidad.nombre

        titulo_area = u'Área Ejecutora:'
        nombre_area = ''

        sec_func = ''

        act_titulo = ''
        act_nombre = ''

    if tipo == 'institucion':
        anio = request.GET.get('anio')
        gerencia = 'Municipalidad'

        titulo_area = u''
        nombre_area = ''

        sec_func = ''

        act_titulo = ''
        act_nombre = ''
        

    output = StringIO.StringIO()

    book = Workbook(output)
    sheet = book.add_worksheet('CUADRO DE NECESIDADES')
    sheet.set_landscape()
    sheet.set_paper(9)

    titulo = book.add_format({
        'bold': 1,
        'align': 'center'
    })

    negrita = book.add_format({'bold': 1})
    fecha = book.add_format({'num_format': 'dd/mm/yy'})
    dinero = book.add_format({'num_format': '0.00'})
    dinero_item = book.add_format({'num_format': '0.00', 'fg_color': '#BADDF5'})
    item = book.add_format({'fg_color': '#BADDF5'})

    wrap = book.add_format({'text_wrap': True})

    negrita_borde = book.add_format({'bold': 1, 'border': 1, 'fg_color': '#BADDF5', 'valign': 'vcenter', 'text_wrap': True, 'align': 'center'})
    borde = book.add_format({'border': 1})
    borde_numero = book.add_format({'border': 1, 'num_format': '0.00'})
    borde_fecha = book.add_format({'num_format': 'dd/mm/yy', 'border': 1})


    hasta = 'U'

    sheet.merge_range('A1:%s1' % hasta, 'MUNICIPALIDAD PROVINCIAL DE URUBAMBA', titulo)
    sheet.merge_range('A2:%s2' % hasta, u'CUADRO DE NECESIDADES DE BIENES, SERVICIOS Y OBRAS PARA EL AÑO FISCAL %s ' % anio, titulo)

    sheet.write('A3', 'Gerencia:', negrita)
    sheet.merge_range('B3:H3', gerencia)

    sheet.write('A4', titulo_area, negrita)
    sheet.merge_range('B4:H4', nombre_area)

    sheet.write('A5', 'SEC FUNC', negrita)
    sheet.merge_range('B5:H5', sec_func)

    sheet.write('A6', act_titulo, negrita)
    sheet.merge_range('B6:H6', act_nombre)

    sheet.write('A8', u'N°', negrita_borde)
    sheet.write('B8', u'Unidad', negrita_borde)
    sheet.write('C8', u'Clasificador', negrita_borde)
    sheet.write('D8', u'Descripción', negrita_borde)
    sheet.write('E8', u'Ene', negrita_borde)
    sheet.write('F8', u'Feb', negrita_borde)
    sheet.write('G8', u'Mar', negrita_borde)
    sheet.write('H8', u'Abr', negrita_borde)
    sheet.write('I8', u'May', negrita_borde)
    sheet.write('J8', u'Jun', negrita_borde)
    sheet.write('K8', u'Jul', negrita_borde)
    sheet.write('L8', u'Ago', negrita_borde)
    sheet.write('M8', u'Set', negrita_borde)
    sheet.write('N8', u'Oct', negrita_borde)
    sheet.write('O8', u'Nov', negrita_borde)
    sheet.write('P8', u'Dic', negrita_borde)
    sheet.write('Q8', u'Total', negrita_borde)
    sheet.write('R8', u'Precio', negrita_borde)
    sheet.write('S8', u'Total S/', negrita_borde)
    sheet.write('T8', u'Dependencia', negrita_borde)
    sheet.write('U8', u'Unidad organica', negrita_borde)

    k = 9
    item = 1
    first = k

    if tipo == 'cuadro':
        detalles = cuadro[0].cuadrodetalle_set.all()
    if tipo == 'plan':
        detalles = CuadroDetalle.objects.filter(pertenece_a__actividad__pertenece_a = plan.pk)
    if tipo == 'dependencia':
        detalles = CuadroDetalle.objects.filter(pertenece_a__actividad__pertenece_a__area_ejecutora = unidad.pk, pertenece_a__actividad__pertenece_a__anio = anio)
    if tipo == 'organica':
        detalles = CuadroDetalle.objects.filter(pertenece_a__actividad__pertenece_a__unidad_organica = unidad.pk, pertenece_a__actividad__pertenece_a__anio = anio)
    if tipo == 'institucion':
        detalles = CuadroDetalle.objects.filter(pertenece_a__actividad__pertenece_a__anio = anio)
        
    for detalle in detalles:
        sheet.write('A%s' % k, item, borde)
        sheet.write('B%s' % k, detalle.unidad_medida, borde)
        sheet.write('C%s' % k, detalle.clasificador.cadena, borde)
        sheet.write('D%s' % k, detalle.producto.descripcion, borde)
        sheet.write('E%s' % k, detalle.p1, borde_numero)
        sheet.write('F%s' % k, detalle.p2, borde_numero)
        sheet.write('G%s' % k, detalle.p3, borde_numero)
        sheet.write('H%s' % k, detalle.p4, borde_numero)
        sheet.write('I%s' % k, detalle.p5, borde_numero)
        sheet.write('J%s' % k, detalle.p6, borde_numero)
        sheet.write('K%s' % k, detalle.p7, borde_numero)
        sheet.write('L%s' % k, detalle.p8, borde_numero)
        sheet.write('M%s' % k, detalle.p9, borde_numero)
        sheet.write('N%s' % k, detalle.p10, borde_numero)
        sheet.write('O%s' % k, detalle.p11, borde_numero)
        sheet.write('P%s' % k, detalle.p12, borde_numero)
        formula = '=SUM(E{0}:P{0})'.format(k)
        sheet.write_formula('Q%s' % k, formula, borde_numero)
        sheet.write('R%s' % k, detalle.precio, borde_numero)
        formula2 = '=Q{0}*R{0}'.format(k)
        sheet.write_formula('S%s' % k, formula2, borde_numero)

        if detalle.pertenece_a.actividad.pertenece_a.area_ejecutora is not None:
            dependencia = detalle.pertenece_a.actividad.pertenece_a.area_ejecutora.nombre
        else:
            dependencia = ''

        if detalle.pertenece_a.actividad.pertenece_a.unidad_organica is not None:
            organica = detalle.pertenece_a.actividad.pertenece_a.unidad_organica.nombre
        else:
            organica = ''

        sheet.write('T%s' % k, dependencia)
        sheet.write('U%s' % k, organica)
        item = item + 1
        k = k + 1


    sheet.write('R%s' % k, 'TOTAL S/', borde)
    formula3 = '=SUM(S%s:S%s)' % (first, k-1)
    sheet.write_formula('S%s' % k, formula3, borde_numero)
    sheet.autofilter('A8:S%s' % (k-1))



    book.close()

    output.seek(0)
    response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = "attachment; filename=cuadro.xlsx"

    return response

@login_required
def resumen_excel(request):
    output = StringIO.StringIO()

    book = Workbook(output)
    sheet = book.add_worksheet(u'Resumen por unidad orgánica')
    sheet.set_landscape()
    sheet.set_paper(9)

    titulo = book.add_format({
        'bold': 1,
        'align': 'center'
    })

    negrita = book.add_format({'bold': 1})
    fecha = book.add_format({'num_format': 'dd/mm/yy'})
    dinero = book.add_format({'num_format': '0.00'})
    dinero_item = book.add_format({'num_format': '0.00', 'fg_color': '#BADDF5'})
    item = book.add_format({'fg_color': '#BADDF5'})

    wrap = book.add_format({'text_wrap': True})

    negrita_borde = book.add_format({'bold': 1, 'border': 1, 'fg_color': '#BADDF5', 'valign': 'vcenter', 'text_wrap': True, 'align': 'center'})
    borde = book.add_format({'border': 1})
    borde_numero = book.add_format({'border': 1, 'num_format': '0.00'})
    borde_fecha = book.add_format({'num_format': 'dd/mm/yy', 'border': 1})

    anio = request.GET.get('anio')

    sheet.write('A3', u'Unidades orgánicas', negrita_borde)

    from base.models import AsignacionPresupuestal
    alfabeto = ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T','U']

    k = 0
    for fuente in AsignacionPresupuestal.objects.all():
        sheet.write('%s3' % alfabeto[k], fuente.rubro, negrita_borde)
        k = k + 1

    sheet.write('%s3' % alfabeto[k], 'Total', negrita_borde)

    hasta = alfabeto[k]

    sheet.merge_range('A1:%s1' % hasta, 'MUNICIPALIDAD PROVINCIAL DE URUBAMBA', titulo)
    sheet.merge_range('A2:%s2' % hasta, u'RESUMEN DE UNIDADES ORGÁNICAS PARA EL AÑO FISCAL %s ' % anio, titulo)

    j = 4
    for organica in UnidadOrganica.objects.all():
        sheet.write('A%s' % j, organica.nombre, negrita)
        k = 0
        for fuente in AsignacionPresupuestal.objects.all():
            total = traer_suma(fuente, organica, 'o')
            sheet.write('%s%s' % (alfabeto[k], j), total, dinero)
            k = k + 1
        sheet.write_formula('%s%s' % (alfabeto[k], j),'=SUM(B%s:%s%s)' % (j, alfabeto[k-1], j) ,dinero)
        j = j + 1
        for unidad in Unidad.objects.filter(pertenece_a = organica):
            sheet.write('A%s' % j, unidad.nombre)
            l = 0
            for fuente in AsignacionPresupuestal.objects.all():
                total = traer_suma(fuente, unidad, 'u')
                sheet.write('%s%s' % (alfabeto[l], j), total, dinero)
                l = l + 1
            sheet.write_formula('%s%s' % (alfabeto[l], j),'=SUM(B%s:%s%s)' % (j, alfabeto[l-1], j) ,dinero)
            j = j + 1

    sheet.write('A%s' % j, 'TOTAL', negrita_borde)

    k = 0
    for fuente in AsignacionPresupuestal.objects.all():
        sheet.write_formula('%s%s' % (alfabeto[k], j),'=SUM(%s4:%s%s)' % (alfabeto[k], alfabeto[k], j-1) ,dinero)
        k = k + 1

    sheet.write_formula('%s%s' % (alfabeto[k], j),'=SUM(%s4:%s%s)' % (alfabeto[k], alfabeto[k], j-1) ,dinero)


    book.close()

    output.seek(0)
    response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = "attachment; filename=resumen.xlsx"

    return response