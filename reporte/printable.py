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

def negrita_custom_center(size):
    return ParagraphStyle(
        name = 'negrita_custom_center_%s' % str(size),
        fontName = 'Helvetica-Bold',
        fontSize = size,
        alignment = TA_CENTER
    )


def tabla_plan(plan):
    total = plan.actividad_set.count()
    return TableStyle(
            [
                ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                ('ALIGNMENT', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('ALIGNMENT', (1,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,1), 'Helvetica-Bold'),
                ('ALIGNMENT', (0,0), (4,0), 'CENTER'),
                ('VALIGN', (0,0), (-1,1), 'MIDDLE'),
                ('SPAN', (0,0), (0,1)), # Codigo
                ('SPAN', (1,0), (1,1)), # Tarea
                ('SPAN', (2,0), (2,1)), # Medida
                ('SPAN', (4,0), (7,0)), # Meta
                ('SPAN', (8,0), (8,1)), # Total
                ('SPAN', (9,0), (9,1)), # Fecha
                ('SPAN', (10,0), (10,1)), # Dist.
                ('SPAN', (11,0), (11,1)), # Fuente
                ('SPAN', (0,total + 2), (8,total + 2)),
            ]
        )

def tabla_plan_meses(plan):
    total = plan.actividad_set.count()
    return TableStyle(
            [
                ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                ('ALIGNMENT', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('ALIGNMENT', (1,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,1), 'Helvetica-Bold'),
                ('ALIGNMENT', (0,0), (4,0), 'CENTER'),
                ('VALIGN', (0,0), (-1,1), 'MIDDLE'),
                ('SPAN', (0,0), (0,1)), # Codigo
                ('SPAN', (1,0), (1,1)), # Tarea
                ('SPAN', (2,0), (2,1)), # Medida
                ('SPAN', (4,0), (15,0)), # Meta
                ('SPAN', (16,0), (16,1)), # Total
                ('SPAN', (17,0), (17,1)), # Fecha
                ('SPAN', (18,0), (18,1)), # Dist.
                ('SPAN', (19,0), (19,1)), # Fuente
                ('SPAN', (0,total + 2), (16,total + 2)),
            ]
        )


class ImpresionPlan:
  def __init__(self, buffer, pagesize):
    self.buffer = buffer
    if pagesize == 'A4':
      self.pagesize = landscape(A4)
    elif pagesize == 'Letter':
      self.pagesize = landscape(letter)
      self.width, self.height = self.pagesize

  @staticmethod
  def _header_footer_plan(canvas, doc, plan):
    canvas.saveState()

    logo = 'reporte/static/reporte/logo.jpg'

    canvas.drawImage(logo, doc.leftMargin + 72 * mm, doc.height + doc.topMargin - 12 * mm, width = (1.8 * cm), height = (1.8 * cm))
    

    # Cabecera
    header = Paragraph(u'Municipalidad Provincial de Urubamba', negrita_custom_center(15))
    w, h = header.wrap(doc.width, doc.topMargin)
    header.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin)


    header = Paragraph(u'Trabajos por Unidad Orgánica', negrita_custom_center(12))
    w, h = header.wrap(doc.width, doc.topMargin)
    header.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - 8 * mm)


    header = Paragraph(u'<strong>Unidad Orgánica</strong>: %s <strong>Área Ejecutora</strong>: %s <strong>Responsable</strong>: %s' % (plan.unidad_organica, plan.area_ejecutora, plan.responsable), normal_custom(9))
    w, h = header.wrap(doc.width, doc.topMargin)
    header.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - 15 * mm - h)

    canvas.restoreState()


  def print_plan(self, plan):
    buffer = self.buffer
    doc = SimpleDocTemplate(buffer, pagesize = self.pagesize, topMargin = 35 * mm, leftMargin = 8 * mm , rightMargin = 8 * mm, bottomMargin = 8 * mm, showBoundary = 1)

    elements  = []

    spacer = 5
    elements.append(Paragraph(u'<strong>Acción Central</strong>: %s' % plan.accion_central, normal_custom(9)))
    elements.append(Spacer(0, spacer))

    elements.append(Paragraph(u'<strong>Objetivo General Institucional</strong>: %s' % plan.objetivo_general_institucional, normal_custom(9)))
    elements.append(Spacer(0, spacer))

    elements.append(Paragraph(u'<strong>Objetivo Específico Institucional</strong>: %s' % plan.objetivo_especifico_institucional, normal_custom(9)))
    elements.append(Spacer(0, spacer))

    if plan.periodo == '1':

        detalles_data = [
            [u'Código', Paragraph('Tarea o Actividad', negrita_custom_center(9)), 'U. de Medida', 'Peso', 'Meta %', '', '', '', 'Total periodos %', u'F. de término', u'Dist. Pres.', 'Fuente'],
            ['', '', '', 'De la tarea', 'T1', 'T2', 'T3', 'T4', '', '', '', '']
        ]

        primero = 1
        for actividad in plan.actividad_set.all():
            codigo = Paragraph(str(primero), normal_custom_right(9))
            tarea = Paragraph(actividad.tarea_actividad, normal_custom(9))
            medida = Paragraph(actividad.unidad_medida.nombre, normal_custom_center(9))
            peso = Paragraph(str(actividad.peso), normal_custom_center(9))
            t1 = Paragraph(str(actividad.t1), normal_custom_center(9))
            t2 = Paragraph(str(actividad.t2), normal_custom_center(9))
            t3 = Paragraph(str(actividad.t3), normal_custom_center(9))
            t4 = Paragraph(str(actividad.t4), normal_custom_center(9))
            total = Paragraph(str(actividad.total), normal_custom_center(9))
            fecha = Paragraph(actividad.fecha_termino.strftime('%d/%m/%Y'), normal_custom_center(9))
            distribucion = Paragraph(number_format(actividad.distribucion_presupuestal, 2), normal_custom_right(9))
            fuente = Paragraph(actividad.asignacion_presupuestal.rubro, normal_custom(9))

            detalles_data.append(
                [codigo, tarea, medida, peso, t1, t2, t3, t4, total, fecha, distribucion, fuente]
            )

            primero += 1

        presupuesto = Paragraph(number_format(plan.presupuesto, 2), normal_custom_right(9))
        detalles_data.append(
            ['', '', '', '', '', '', '', '', '', 'Total S/', presupuesto, '']   
        )


        detalles_tabla = Table(detalles_data, colWidths = [15 * mm, 70 * mm, None], repeatRows = 2, style = tabla_plan(plan))

    else:
        detalles_data = [
            [u'Código', 'Tarea o Actividad', 'U. de Medida', 'Peso', 'Meta %', '', '', '', '', '', '', '', '', '', '', '', 'Total periodos %', u'F. de término', u'Dist. Pres.', 'Fuente'],
            ['', '', '', 'De la tarea', 'T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9', 'T10', 'T11', 'T12', '', '', '', '']
        ]

        primero = 1
        for actividad in plan.actividad_set.all():
            codigo = Paragraph(str(primero), normal_custom_right(8))
            tarea = Paragraph(actividad.tarea_actividad, normal_custom(8))
            medida = Paragraph(actividad.unidad_medida.nombre, normal_custom_center(8))
            peso = Paragraph(str(actividad.peso), normal_custom_center(8))
            t1 = Paragraph(str(actividad.t1), normal_custom_center(8))
            t2 = Paragraph(str(actividad.t2), normal_custom_center(8))
            t3 = Paragraph(str(actividad.t3), normal_custom_center(8))
            t4 = Paragraph(str(actividad.t4), normal_custom_center(8))
            t5 = Paragraph(str(actividad.t5), normal_custom_center(8))
            t6 = Paragraph(str(actividad.t6), normal_custom_center(8))
            t7 = Paragraph(str(actividad.t7), normal_custom_center(8))
            t8 = Paragraph(str(actividad.t8), normal_custom_center(8))
            t9 = Paragraph(str(actividad.t9), normal_custom_center(8))
            t10 = Paragraph(str(actividad.t10), normal_custom_center(8))
            t11 = Paragraph(str(actividad.t11), normal_custom_center(8))
            t12 = Paragraph(str(actividad.t12), normal_custom_center(8))
            total = Paragraph(str(actividad.total), normal_custom_center(8))
            fecha = Paragraph(actividad.fecha_termino.strftime('%d/%m/%Y'), normal_custom_center(8))
            distribucion = Paragraph(number_format(actividad.distribucion_presupuestal, 2), normal_custom_right(8))
            fuente = Paragraph(actividad.asignacion_presupuestal.rubro, normal_custom(8))

            detalles_data.append(
                [codigo, tarea, medida, peso, t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12, total, fecha, distribucion, fuente]
            )

            primero += 1

        presupuesto = Paragraph(number_format(plan.presupuesto, 2), normal_custom_right(9))
        detalles_data.append(
            ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 'Total S/', presupuesto, '']   
        )


        detalles_tabla = Table(detalles_data, colWidths = [15 * mm, 50 * mm, 25 * mm, 20 * mm, 10 * mm, 10 * mm, 10 * mm, 10 * mm, 10 * mm, 10 * mm, 10 * mm, 10 * mm, 10 * mm, 10 * mm, 10 * mm, 10 * mm, 20 * mm, None], repeatRows = 2, style = tabla_plan_meses(plan))

    elements.append(detalles_tabla)


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
    self.setFont('Helvetica', 9)
    self.drawRightString(205 * mm, 286 * mm,
      u"Página %d de %d" % (self._pageNumber, page_count))
