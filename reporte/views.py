# -*- coding: utf-8 -*-
from io import BytesIO

from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.contrib import messages
from django.core.urlresolvers import reverse

from plan.models import Plan
from printable import ImpresionPlan
from plan.utils import solo_responsable, grupo_administrador, grupo_logistico

from base.models import Unidad, UnidadOrganica

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
@user_passes_test(grupo_administrador)
def reporte_dependencia_excel(request):
    unidad = request.POST.get('unidad')
    anio = request.POST.get('anio')
    tipo = request.POST.get('tipo')

    if tipo == 'dependencia':
        oficina = Unidad.objects.get(pk = unidad)
        planes = Plan.objects.filter(area_ejecutora = oficina, anio = anio)
        nombre = oficina.nombre
        titulo_hoja = 'Trabajos por Dependencia'
    elif tipo == 'organica':
        unidad_organica = UnidadOrganica.objects.get(pk = unidad)
        planes = Plan.objects.filter(unidad_organica = unidad_organica, anio = anio)
        nombre = unidad_organica.nombre
        titulo_hoja = u'Trabajos por Unidad Orgánica'
    elif tipo == 'institucion':
        planes = Plan.objects.filter(anio = anio)
        nombre = 'Municipalidad'
        titulo_hoja = u'Trabajos por Institución'
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
    sheet = book.add_worksheet(nombre)
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

        sheet.write('A%s' % k, u'Area Ejecutora', negrita)
        sheet.merge_range('B%s:H%s' % (k, k), plan.area_ejecutora.nombre)
        
        sheet.write('I%s' % k, u'Año', negrita)
        sheet.merge_range('J%s:M%s' % (k, k), plan.anio)
        k += 1

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

        inicio = k + 4
        sheet.merge_range('A%s:A%s' % (k, k+3), u'Tarea o Actividad', negrita_borde)
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