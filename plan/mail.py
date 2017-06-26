# -*- coding: utf-8 -*-

from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User, Group

def notificar_plan(plan):

    admins = User.objects.filter(groups = 1)

    emails = []

    for admin in admins:
        emails.append(admin.email)

    mensaje = 'Estimado (a) Administrador:\n\n'

    mensaje += 'El usuario %s ha creado un plan en el aplicativo POI de la Municipalidad de Urubamba.\n' % (plan.creado_por)
    mensaje += u'Para poder verlo, ingrese a la siguiente dirección:\n\n'

    mensaje += 'http://poi.muniurubamba.gob.pe/plan/ver/%s\n\n' % plan.pk

    mensaje += '--\n'
    mensaje += 'Sistema POI - MPU\n'
    mensaje += u'Este ha sido un envío automático, por favor no responda este correo.'

    send_mail(u'Nuevo Plan Operativo', mensaje, 'POI - MPU <no-reply@abastecimiento.pe>', emails)  

def notificar_cuadro(cuadro):

    admins = User.objects.filter(groups = 2)

    emails = []

    for admin in admins:
        emails.append(admin.email)

    mensaje = u'Estimado (a) Logístico:\n\n'

    mensaje += 'El usuario %s ha creado un cuadro de necesidades en el aplicativo POI de la Municipalidad de Urubamba.\n' % (cuadro.creado_por)
    mensaje += u'Para poder verlo, ingrese a la siguiente dirección:\n\n'

    mensaje += 'http://poi.muniurubamba.gob.pe/cuadro/editar/%s\n\n' % cuadro.pk

    mensaje += '--\n'
    mensaje += 'Sistema POI - MPU\n'
    mensaje += u'Este ha sido un envío automático, por favor no responda este correo.'

    send_mail(u'Nuevo Cuadro de Necesidades', mensaje, 'POI - MPU <no-reply@abastecimiento.pe>', emails)
