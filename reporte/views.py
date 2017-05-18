# -*- coding: utf-8 -*-
from io import BytesIO

from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.contrib import messages
from django.core.urlresolvers import reverse

from plan.models import Plan
from printable import ImpresionPlan
from plan.utils import solo_responsable


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
