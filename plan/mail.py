# -*- coding: utf-8 -*-

from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User, Group

def notificar_plan(plan):

    admins = User.objects.filter(groups = 1)

    for admin in admins:

        mensaje = 'Estimado (a) %s:' % admin.get_full_name()

        mensaje += 'El usuario %s ha creado un plan en el aplicativo POI de la Municipalidad de Urubamba.' % (plan.creado_por)
        mensaje += u'Para poder verlo, ingrese a la siguiente dirección:'

        mensaje += 'http://poi.muniurubamba.gob.pe/plan/ver/%s' % plan.pk

        mensaje += '--'
        mensaje += 'Sistema POI - MPU'
        mensaje += u'Este ha sido un envío automático, por favor no responda este correo.'

        send_mail(u'Nuevo Plan Operativo', mensaje, 'POI - MPU <no-reply@abastecimiento.pe>', [admin.email])  

def notificar_cuadro(cuadro):

    admins = User.objects.filter(groups = 2)

    for admin in admins:

        mensaje = 'Estimado (a) %s:' % admin.get_full_name()

        mensaje += 'El usuario %s ha creado un cuadro de necesidades en el aplicativo POI de la Municipalidad de Urubamba.' % (cuadro.creado_por)
        mensaje += u'Para poder verlo, ingrese a la siguiente dirección:'

        mensaje += 'http://poi.muniurubamba.gob.pe/cuadro/editar/%s' % cuadro.pk

        mensaje += '--'
        mensaje += 'Sistema POI - MPU'
        mensaje += u'Este ha sido un envío automático, por favor no responda este correo.'

        send_mail(u'Nuevo Cuadro de Necesidades', mensaje, 'POI - MPU <no-reply@abastecimiento.pe>', [admin.email])  


