# -*- coding: utf-8 -*-

from functools import partial
import datetime

from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib.units import inch, mm, cm
from reportlab.lib import colors

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from django.contrib.auth.models import User
from django.conf import settings

from plan.models import Plan


def number_format(number, decimals=0, dec_point='.', thousands_sep=','):
    try:
        number = round(float(number), decimals)
    except ValueError:
         return number
    neg = number < 0
    integer, fractional = str(abs(number)).split('.')
    m = len(integer) % 3
    if m:
        parts = [integer[:m]]
    else:
        parts = []
    
    parts.extend([integer[m+t:m+t+3] for t in xrange(0, len(integer[m:]), 3)])
    
    if decimals:
        return '%s%s%s%s' % (
            neg and '-' or '', 
            thousands_sep.join(parts), 
            dec_point, 
            fractional.ljust(decimals, '0')[:decimals]
        )
    else:
        return '%s%s' % (neg and '-' or '', thousands_sep.join(parts))



def normal_custom(size):
    return ParagraphStyle(
        name = 'normal_custom_%s' % str(size),
        fontName = 'Helvetica',
        fontSize = size,
    )

def negrita_custom(size):
    return ParagraphStyle(
        name = 'negrita_custom_%s' % str(size),
        fontName = 'Helvetica-Bold',
        fontSize = size,
    )

def normal_custom_center(size):
    return ParagraphStyle(
        name = 'normal_custom_center_%s' % str(size),
        fontName = 'Helvetica',
        fontSize = size,
        alignment = TA_CENTER
    )

def normal_custom_right(size):
    return ParagraphStyle(
        name = 'normal_custom_center_%s' % str(size),
        fontName = 'Helvetica',
        fontSize = size,
        alignment = TA_RIGHT
    )

def negrita_custom_right(size):
    return ParagraphStyle(
        name = 'negrita_custom_center_%s' % str(size),
        fontName = 'Helvetica-Bold',
        fontSize = size,
        alignment = TA_RIGHT
    )

def negrita_custom_center(size):
    return ParagraphStyle(
        name = 'negrita_custom_center_%s' % str(size),
        fontName = 'Helvetica-Bold',
        fontSize = size,
        alignment = TA_CENTER
    )

def tabla_plan_nuevo(plan):
    total = plan.actividad_set.count()
    return TableStyle(
            [
                ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                ('SPAN', (0,1), (1,3)),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]
        )

def tabla_plan(plan):
    return TableStyle(
            [
                ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                ('ALIGNMENT', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]
        )

def tabla_plan_meses(plan):
    return TableStyle(
            [
                ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                ('ALIGNMENT', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                #('SPAN', (4,4), (4,11)),
                ('LINEBELOW', (4,4), (4,11), 0, colors.white),
                ('LINEAFTER', (4,4), (4,11), 0, colors.white),
            ]
        )

def tabla_firma_estilo():
    return TableStyle(
            [
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
                ('FONTSIZE', (0,0), (-1,-1), 9),
                ('ALIGNMENT', (0,0), (-1,-1), 'CENTER'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 0.5),
                ('TOPPADDING', (0,0), (-1,-1), 0.5),
            ]
        )

def tabla_cuadro(cuadro):
    total = cuadro.cuadrodetalle_set.count()
    return TableStyle(
            [
                ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]
        )

class ImpresionPlan:
  def __init__(self, buffer, pagesize):
    self.buffer = buffer
    if pagesize == 'A4':
      self.pagesize = A4
    elif pagesize == 'Letter':
      self.pagesize = landscape(letter)
      self.width, self.height = self.pagesize

  @staticmethod
  def _header_footer_plan(canvas, doc, plan):
    canvas.saveState()

    logo = 'reporte/static/reporte/logo.jpg'

    top = doc.topMargin + doc.bottomMargin - 8 * mm

    canvas.drawImage(logo, doc.leftMargin + 30 * mm, doc.height + top - 12 * mm, width = (1.8 * cm), height = (1.8 * cm))
    

    # Cabecera
    header = Paragraph(u'Nro: %s - %s' % (plan.numero, plan.anio.nombre), negrita_custom(10))
    w, h = header.wrap(doc.width, top)
    header.drawOn(canvas, doc.leftMargin, doc.height + top)


    header = Paragraph(u'Municipalidad Provincial de Urubamba', negrita_custom_center(15))
    w, h = header.wrap(doc.width, top)
    header.drawOn(canvas, doc.leftMargin, doc.height + top)


    header = Paragraph(u'Trabajos por Unidad Orgánica', negrita_custom_center(12))
    w, h = header.wrap(doc.width, top)
    header.drawOn(canvas, doc.leftMargin, doc.height + top - 8 * mm)

    header = Paragraph(u'<strong>Unidad Orgánica</strong>: %s' % (plan.unidad_organica.nombre), normal_custom(9))
    w, h = header.wrap(doc.width, top)
    header.drawOn(canvas, doc.leftMargin, doc.height + top - 15 * mm - h)

    if plan.area_ejecutora is not None:
        header = Paragraph(u'<strong>Área Ejecutora</strong>: %s' % (plan.area_ejecutora.nombre), normal_custom(9))
    else:
        if plan.proyecto is not None:
            header = Paragraph(u'<strong>Proyecto</strong>: %s' % (plan.proyecto), normal_custom(9))
        else:
            header = Paragraph(u'<strong>Área Ejecutora</strong>: %s' % (plan.unidad_organica.nombre), normal_custom(9))

    w, h = header.wrap(doc.width, top)
    header.drawOn(canvas, doc.leftMargin, doc.height + top - 21 * mm - h)

    if plan.area_ejecutora is not None:
        header = Paragraph(u'<strong>Responsable</strong>: %s' % (plan.responsable), normal_custom(9))
    else:
        if plan.proyecto is not None:
            header = Paragraph(u'<strong>Residente</strong>: %s' % (plan.responsable), normal_custom(9))
        else:
            header = Paragraph(u'<strong>Responsable</strong>: %s' % (plan.responsable), normal_custom(9))
    w, h = header.wrap(doc.width, top)
    header.drawOn(canvas, doc.leftMargin, doc.height + top - 27 * mm - h)


    header = Paragraph(u'<strong>Presupuesto</strong>: S/ %s' % number_format(plan.presupuesto, 2), normal_custom(10))
    w, h = header.wrap(doc.width, top)
    header.drawOn(canvas, doc.leftMargin + 150 * mm, doc.height + top - 27 * mm - h)


    firmas_segundo = [
      ['_____________________________', '',  '_____________________________'],
      [u'Firma del responsable', '', u'Planeamiento Estratégico y Operativo']
    ]

    tabla_firmas_2 = Table(firmas_segundo, colWidths = [doc.width/3.0], style = tabla_firma_estilo())
    w, h = tabla_firmas_2.wrap(doc.width, doc.bottomMargin)
    tabla_firmas_2.drawOn(canvas, doc.leftMargin, h + 10)


    canvas.restoreState()


  def print_plan(self, plan):
    buffer = self.buffer
    doc = SimpleDocTemplate(buffer, pagesize = self.pagesize, topMargin = 41 * mm, leftMargin = 8 * mm , rightMargin = 8 * mm, bottomMargin = 40 * mm, showBoundary = 1)

    elements  = []

    spacer = 5


    if plan.unidad_organica.actividades == True:
        if plan.area_ejecutora is not None:
            elements.append(Paragraph(u'<strong>Actividad</strong>: %s' % (plan.act if plan.act is not None else ''), normal_custom(9)))
            elements.append(Spacer(0, spacer))


    # Tabla
    size = 8
    t_act = Paragraph('Actividad', negrita_custom_center(size))
    t_umed = Paragraph(u'U. Medida', negrita_custom_center(size))
    t_fecha = Paragraph(u'Fecha término', negrita_custom_center(size))
    t_peso = Paragraph(u'Peso %', negrita_custom_center(size))
    t_fuente = Paragraph(u'Fuente', negrita_custom_center(size))
    t_obj = Paragraph(u'Objetivo Estratégico Institucional - OEI', negrita_custom_center(size))
    t_acc = Paragraph(u'Acción Estratégica Instituciónal - AEI', negrita_custom_center(size))


    ts = ['T1','T2','T3','T4']
    meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Set', 'Oct', 'Nov', 'Dic']
    tsp,tsm,mesesp,mesesm = [],[],[],[]
    
    for t in ts:
        tsp.append(Paragraph(t, negrita_custom_center(size)))
        tsm.append(Paragraph('Monto ' + t, negrita_custom_center(size)))

    for mes in meses:
        mesesp.append(Paragraph(mes, negrita_custom_center(size)))
        mesesm.append(Paragraph('Monto' + mes, negrita_custom_center(size)))

    t_total = Paragraph(u'Total Periodos', negrita_custom_center(size))
    t_distri = Paragraph(u'Dist. Presupuestal', negrita_custom_center(size))



    conteo = 1

    for actividad in plan.actividad_set.all():

        
        objetivo = Paragraph(actividad.accion.objetivo.completo, normal_custom(7))
        accion = Paragraph(actividad.accion.completo, normal_custom(7))

        detalles_data = [
            [t_obj],
            [objetivo],
            [t_acc],
            [accion],
        ]

        detalles_tabla = Table(detalles_data, colWidths = [None], style = tabla_plan(plan))
        elements.append(detalles_tabla)

        tarea = Paragraph(actividad.tarea_actividad.upper(), normal_custom(7))
        medida = Paragraph(actividad.unidad_medida, normal_custom_center(size))
        peso = Paragraph(str(actividad.peso), normal_custom_center(size))
        t1 = Paragraph(str(actividad.t1), normal_custom_center(size))
        t2 = Paragraph(str(actividad.t2), normal_custom_center(size))
        t3 = Paragraph(str(actividad.t3), normal_custom_center(size))
        t4 = Paragraph(str(actividad.t4), normal_custom_center(size))
        total = Paragraph(str(actividad.total), normal_custom_center(size))
        fecha = Paragraph(actividad.fecha_termino.strftime('%d/%m/%Y'), normal_custom_center(size))
        distribucion = Paragraph(number_format(actividad.distribucion_presupuestal, 2), normal_custom_right(size))
        fuente = Paragraph(actividad.asignacion_presupuestal.fuente, normal_custom_center(size))

        detalles_data = [
            [conteo, t_act, t_umed, t_fecha],
            [tarea, '', medida, fecha],
            ['', '', t_peso, t_fuente],
            ['', '', peso, fuente]

        ]

        detalles_tabla = Table(detalles_data, colWidths = [10 * mm, 130 * mm, None], style = tabla_plan_nuevo(plan))

        elements.append(detalles_tabla)


        if plan.periodo == '1':

            t1 = Paragraph(str(actividad.t1), normal_custom_center(size))
            t2 = Paragraph(str(actividad.t2), normal_custom_center(size))
            t3 = Paragraph(str(actividad.t3), normal_custom_center(size))
            t4 = Paragraph(str(actividad.t4), normal_custom_center(size))
            total = Paragraph(str(actividad.total), normal_custom_center(size))

            p1 = Paragraph(number_format('S/ ' + str(actividad.p1), 2), normal_custom_center(size))
            p2 = Paragraph(number_format('S/ ' + str(actividad.p2), 2), normal_custom_center(size))
            p3 = Paragraph(number_format('S/ ' + str(actividad.p3), 2), normal_custom_center(size))
            p4 = Paragraph(number_format('S/ ' + str(actividad.p4), 2), normal_custom_center(size))
            distribucion = Paragraph('S/ ' + number_format(actividad.distribucion_presupuestal, 2), normal_custom_center(size))

            detalles_data = [
                [tsp[0], tsp[1], tsp[2], tsp[3], t_total],
                [t1, t2, t3, t4, total],
                [tsm[0], tsm[1], tsm[2], tsm[3], t_distri],
                [p1, p2, p3, p4, distribucion],
            ]

            detalles_tabla = Table(detalles_data, colWidths = [None], style = tabla_plan(plan))
            elements.append(detalles_tabla)

        else:
            t1 = Paragraph(str(actividad.t1), normal_custom_center(size))
            t2 = Paragraph(str(actividad.t2), normal_custom_center(size))
            t3 = Paragraph(str(actividad.t3), normal_custom_center(size))
            t4 = Paragraph(str(actividad.t4), normal_custom_center(size))
            t5 = Paragraph(str(actividad.t5), normal_custom_center(size))
            t6 = Paragraph(str(actividad.t6), normal_custom_center(size))
            t7 = Paragraph(str(actividad.t7), normal_custom_center(size))
            t8 = Paragraph(str(actividad.t8), normal_custom_center(size))
            t9 = Paragraph(str(actividad.t9), normal_custom_center(size))
            t10 = Paragraph(str(actividad.t10), normal_custom_center(size))
            t11 = Paragraph(str(actividad.t11), normal_custom_center(size))
            t12 = Paragraph(str(actividad.t12), normal_custom_center(size))
            total = Paragraph(str(actividad.total), normal_custom_center(size))

            p1 = Paragraph(number_format('S/ ' + str(actividad.p1), 2), normal_custom_center(size))
            p2 = Paragraph(number_format('S/ ' + str(actividad.p2), 2), normal_custom_center(size))
            p3 = Paragraph(number_format('S/ ' + str(actividad.p3), 2), normal_custom_center(size))
            p4 = Paragraph(number_format('S/ ' + str(actividad.p4), 2), normal_custom_center(size))
            p5 = Paragraph(number_format('S/ ' + str(actividad.p5), 2), normal_custom_center(size))
            p6 = Paragraph(number_format('S/ ' + str(actividad.p6), 2), normal_custom_center(size))
            p7 = Paragraph(number_format('S/ ' + str(actividad.p7), 2), normal_custom_center(size))
            p8 = Paragraph(number_format('S/ ' + str(actividad.p8), 2), normal_custom_center(size))
            p9 = Paragraph(number_format('S/ ' + str(actividad.p9), 2), normal_custom_center(size))
            p10 = Paragraph(number_format('S/ ' + str(actividad.p10), 2), normal_custom_center(size))
            p11 = Paragraph(number_format('S/ ' + str(actividad.p11), 2), normal_custom_center(size))
            p12 = Paragraph(number_format('S/ ' + str(actividad.p12), 2), normal_custom_center(size))
            distribucion = Paragraph('S/ ' + number_format(actividad.distribucion_presupuestal, 2), normal_custom_center(size))

            detalles_data = [
                [mesesp[0], mesesp[1], mesesp[2], mesesp[3], t_total],
                [t1, t2, t3, t4, total],
                [mesesm[0], mesesm[1], mesesm[2], mesesm[3], t_distri],
                [p1, p2, p3, p4, distribucion],

                [mesesp[4], mesesp[5], mesesp[6], mesesp[7], ''],
                [t5, t6, t7, t8, ''],
                [mesesm[4], mesesm[5], mesesm[6], mesesm[7], ''],
                [p5, p6, p7, p8, ''],

                [mesesp[8], mesesp[9], mesesp[10], mesesp[11], ''],
                [t9, t10, t11, t12, ''],
                [mesesm[8], mesesm[9], mesesm[10], mesesm[11], ''],
                [p9, p10, p11, p12, ''],
            ]

            detalles_tabla = Table(detalles_data, colWidths = [None], style = tabla_plan_meses(plan))
            elements.append(detalles_tabla)

        conteo = conteo + 1

        elements.append(Spacer(0,2 * mm))


        


    doc.build(elements, onFirstPage = partial(self._header_footer_plan, plan = plan),
      onLaterPages = partial(self._header_footer_plan, plan = plan), canvasmaker = NumberedCanvas)

    pdf = buffer.getvalue()
    buffer.close()
    return pdf

class NumberedCanvas(canvas.Canvas):
  def __init__(self, *args, **kwargs):
    canvas.Canvas.__init__(self, *args, **kwargs)
    self._saved_page_states = []

  def showPage(self):
    self._saved_page_states.append(dict(self.__dict__))
    self._startPage()

  def save(self):
    """add page info to each page (page x of y)"""
    num_pages = len(self._saved_page_states)
    for state in self._saved_page_states:
      self.__dict__.update(state)
      self.draw_page_number(num_pages)
      canvas.Canvas.showPage(self)
      canvas.Canvas.save(self)

  def draw_page_number(self, page_count):
    # Change the position of this to wherever you want the page number to be
    self.setFont('Helvetica', 8)
    self.drawRightString(205 * mm, 290 * mm,
      u"Página %d de %d" % (self._pageNumber, page_count))


class ImpresionCuadro:
  def __init__(self, buffer, pagesize):
    self.buffer = buffer
    if pagesize == 'A4':
      self.pagesize = landscape(A4)
    elif pagesize == 'Letter':
      self.pagesize = landscape(letter)
      self.width, self.height = self.pagesize

  @staticmethod
  def _header_footer_cuadro(canvas, doc, cuadro):
    canvas.saveState()

    logo = 'reporte/static/reporte/logo.jpg'

    top = doc.topMargin + doc.bottomMargin - 8 * mm

    canvas.drawImage(logo, doc.leftMargin + 30 * mm, doc.height + top - 12 * mm, width = (1.8 * cm), height = (1.8 * cm))
    

    # Cabecera
    header = Paragraph(u'Municipalidad Provincial de Urubamba', negrita_custom_center(15))
    w, h = header.wrap(doc.width, top)
    header.drawOn(canvas, doc.leftMargin, doc.height + top)


    header = Paragraph(u'Cuadro de necesidades', negrita_custom_center(12))
    w, h = header.wrap(doc.width, top)
    header.drawOn(canvas, doc.leftMargin, doc.height + top - 8 * mm)

    header = Paragraph(u'<strong>Unidad Orgánica</strong>: %s' % (cuadro.actividad.pertenece_a.unidad_organica.nombre), normal_custom(9))
    w, h = header.wrap(doc.width, top)
    header.drawOn(canvas, doc.leftMargin, doc.height + top - 15 * mm - h)

    if cuadro.actividad.pertenece_a.area_ejecutora is not None:
        header = Paragraph(u'<strong>Área Ejecutora</strong>: %s' % (cuadro.actividad.pertenece_a.area_ejecutora.nombre), normal_custom(9))
    else:
        if cuadro.actividad.pertenece_a.proyecto is not None:
            header = Paragraph(u'<strong>Proyecto</strong>: %s' % (cuadro.actividad.pertenece_a.proyecto), normal_custom(9))
        else:
            header = Paragraph(u'<strong>Área Ejecutora</strong>: %s' % (cuadro.actividad.pertenece_a.unidad_organica.nombre), normal_custom(9))

    w, h = header.wrap(doc.width, top)
    header.drawOn(canvas, doc.leftMargin, doc.height + top - 21 * mm - h)

    if cuadro.actividad.pertenece_a.area_ejecutora is not None:
        header = Paragraph(u'<strong>Responsable</strong>: %s' % (cuadro.actividad.pertenece_a.responsable), normal_custom(9))
    else:
        if cuadro.actividad.pertenece_a.proyecto is not None:
            header = Paragraph(u'<strong>Residente</strong>: %s' % (cuadro.actividad.pertenece_a.responsable), normal_custom(9))
        else:
            header = Paragraph(u'<strong>Responsable</strong>: %s' % (cuadro.actividad.pertenece_a.responsable), normal_custom(9))
    w, h = header.wrap(doc.width, top)
    header.drawOn(canvas, doc.leftMargin, doc.height + top - 27 * mm - h)


    header = Paragraph(u'<strong>Presupuesto</strong>: S/ %s' % number_format(cuadro.actividad.distribucion_presupuestal, 2), normal_custom(10))
    w, h = header.wrap(doc.width, top)
    header.drawOn(canvas, doc.leftMargin + 150 * mm, doc.height + top - 27 * mm - h)


    firmas_segundo = [
      ['_____________________________', '_____________________________',  '_____________________________'],
      [u'Firma del responsable', 'Jefe inmediato', 'Gerencia Municipal']
    ]

    tabla_firmas_2 = Table(firmas_segundo, colWidths = [doc.width/3.0], style = tabla_firma_estilo())
    w, h = tabla_firmas_2.wrap(doc.width, doc.bottomMargin)
    tabla_firmas_2.drawOn(canvas, doc.leftMargin, h + 10)


    canvas.restoreState()


  def print_cuadro(self, cuadro):
    buffer = self.buffer
    doc = SimpleDocTemplate(buffer, pagesize = self.pagesize, topMargin = 41 * mm, leftMargin = 8 * mm , rightMargin = 8 * mm, bottomMargin = 40 * mm, showBoundary = 1)

    elements  = []

    spacer = 5
    elements.append(Paragraph(u'<strong>Actividad</strong>: %s' % cuadro.actividad.tarea_actividad.upper(), normal_custom(9)))
    elements.append(Spacer(0, spacer))

    # Tabla.
    size = 8
    size2 = 6
    t_item = Paragraph('#', negrita_custom_center(size))
    t_desc = Paragraph(u'Descripción', negrita_custom_center(size))
    t_umed = Paragraph(u'U. Med.', negrita_custom_center(size))
    t_clas = Paragraph(u'Clas.', negrita_custom_center(size))
    t_t1 = Paragraph(u'T1', negrita_custom_center(size))
    t_t2 = Paragraph(u'T2', negrita_custom_center(size))
    t_t3 = Paragraph(u'T3', negrita_custom_center(size))
    t_t4 = Paragraph(u'T4', negrita_custom_center(size))

    t_e = Paragraph(u'Ene', negrita_custom_center(size))
    t_f = Paragraph(u'Feb', negrita_custom_center(size))
    t_m = Paragraph(u'Mar', negrita_custom_center(size))
    t_a = Paragraph(u'Abr', negrita_custom_center(size))
    t_y = Paragraph(u'May', negrita_custom_center(size))
    t_j = Paragraph(u'Jun', negrita_custom_center(size))
    t_l = Paragraph(u'Jul', negrita_custom_center(size))
    t_g = Paragraph(u'Ago', negrita_custom_center(size))
    t_s = Paragraph(u'Set', negrita_custom_center(size))
    t_o = Paragraph(u'Oct', negrita_custom_center(size))
    t_n = Paragraph(u'Nov', negrita_custom_center(size))
    t_d = Paragraph(u'Dic', negrita_custom_center(size))
    
    t_total = Paragraph(u'Total', negrita_custom_center(size))
    t_totalprecio = Paragraph(u'Precio', negrita_custom_center(size))
    t_totalsoles = Paragraph(u'Total S/', negrita_custom_center(size))

    if cuadro.actividad.pertenece_a.periodo == '1':
        detalles_data = [
            [t_item, t_umed, t_clas, t_desc, t_t1, t_t2, t_t3, t_t4, t_total, t_totalprecio, t_totalsoles]
        ]

        k = 1
        for detalle in cuadro.cuadrodetalle_set.all():
            kk = Paragraph(str(k), normal_custom_center(size))
            u_med = Paragraph(detalle.unidad_medida, normal_custom(size))
            clas = Paragraph(detalle.clasificador.cadena, normal_custom(size))
            desc = Paragraph(detalle.producto.descripcion, normal_custom(size))
            p1 = Paragraph(str(detalle.p1), normal_custom_right(size))
            p4 = Paragraph(str(detalle.p4), normal_custom_right(size))
            p7 = Paragraph(str(detalle.p7), normal_custom_right(size))
            p10 = Paragraph(str(detalle.p10), normal_custom_right(size))
            total_cantidades = Paragraph(str(detalle.total_cantidades), normal_custom_right(size))
            precio = Paragraph(number_format(detalle.precio, 2), normal_custom_right(size))
            total = Paragraph(number_format(detalle.total, 2), normal_custom_right(size))
            detalles_data.append(
                [kk, u_med, clas, desc, p1, p4, p7, p10, total_cantidades, precio, total]
            )
            k = k+1

        t_texto = Paragraph('TOTAL S/', negrita_custom_right(size))
        super_total = Paragraph(number_format(cuadro.total, 2), negrita_custom_right(size))
        detalles_data.append(
          ['--', '--', '--', '--', '--', '--', '--', t_texto, super_total]
        )

        widths = [10 * mm, 15 * mm, 20 * mm, 85 * mm, None]
    else:
        detalles_data = [
            [t_item, t_umed, t_clas, t_desc, t_e, t_f, t_m, t_a, t_y, t_j, t_l, t_g, t_s, t_o, t_n, t_d, t_total, t_totalprecio, t_totalsoles]
        ]

        k = 1
        for detalle in cuadro.cuadrodetalle_set.all():
            kk = Paragraph(str(k), normal_custom_center(size2))
            u_med = Paragraph(detalle.unidad_medida, normal_custom(size))
            clas = Paragraph(detalle.clasificador.cadena, normal_custom(size))
            desc = Paragraph(detalle.producto.descripcion, normal_custom(size2))
            p1 = Paragraph(str(detalle.p1), normal_custom_right(size2))
            p2 = Paragraph(str(detalle.p2), normal_custom_right(size2))
            p3 = Paragraph(str(detalle.p3), normal_custom_right(size2))
            p4 = Paragraph(str(detalle.p4), normal_custom_right(size2))
            p5 = Paragraph(str(detalle.p5), normal_custom_right(size2))
            p6 = Paragraph(str(detalle.p6), normal_custom_right(size2))
            p7 = Paragraph(str(detalle.p7), normal_custom_right(size2))
            p8 = Paragraph(str(detalle.p8), normal_custom_right(size2))
            p9 = Paragraph(str(detalle.p9), normal_custom_right(size2))
            p10 = Paragraph(str(detalle.p10), normal_custom_right(size2))
            p11 = Paragraph(str(detalle.p11), normal_custom_right(size2))
            p12 = Paragraph(str(detalle.p12), normal_custom_right(size2))
            total_cantidades = Paragraph(str(detalle.total_cantidades), normal_custom_right(size2))
            precio = Paragraph(number_format(detalle.precio, 2), normal_custom_right(size2))
            total = Paragraph(number_format(detalle.total, 2), normal_custom_right(size2))
            detalles_data.append(
                [kk, u_med, clas, desc, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, total_cantidades, precio, total]
            )
            k = k+1

        t_texto = Paragraph('TOTAL S/', negrita_custom_right(size2))
        super_total = Paragraph(number_format(cuadro.total, 2), negrita_custom_right(size2))
        detalles_data.append(
          ['--', '--', '--', '--', '--', '--', '--', '--', '--', '--', '--', '--', '--', '--', '--', t_texto, super_total]
        )

        widths = [8 * mm,  15 * mm, 20 * mm, 17 * mm, None]


    detalles_tabla = Table(detalles_data, colWidths = widths, style=tabla_cuadro(cuadro))
    elements.append(detalles_tabla)

 

        


    doc.build(elements, onFirstPage = partial(self._header_footer_cuadro, cuadro = cuadro),
      onLaterPages = partial(self._header_footer_cuadro, cuadro = cuadro), canvasmaker = NumberedCuadroCanvas)

    pdf = buffer.getvalue()
    buffer.close()
    return pdf

class NumberedCuadroCanvas(canvas.Canvas):
  def __init__(self, *args, **kwargs):
    canvas.Canvas.__init__(self, *args, **kwargs)
    self._saved_page_states = []

  def showPage(self):
    self._saved_page_states.append(dict(self.__dict__))
    self._startPage()

  def save(self):
    """add page info to each page (page x of y)"""
    num_pages = len(self._saved_page_states)
    for state in self._saved_page_states:
      self.__dict__.update(state)
      self.draw_page_number(num_pages)
      canvas.Canvas.showPage(self)
      canvas.Canvas.save(self)

  def draw_page_number(self, page_count):
    # Change the position of this to wherever you want the page number to be
    self.setFont('Helvetica', 8)
    self.drawRightString(205 * mm, 290 * mm,
      u"Página %d de %d" % (self._pageNumber, page_count))
