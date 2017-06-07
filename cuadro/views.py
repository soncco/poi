# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, user_passes_test

from .models import Cuadro, CuadroDetalle, Producto
from .forms import CuadroForm, CuadroDetalleFormSet
from .serializers import ProductoSerializer
from plan.models import Actividad

from rest_framework import viewsets, generics


import json, datetime

@login_required
def nuevo_cuadro(request, id):
    actividad = Actividad.objects.get(pk = id)
    form = CuadroForm()
    detalle_form = CuadroDetalleFormSet()
    context = {'actividad': actividad, 'form': form, 'detalle_form': detalle_form}
    return render(request, 'cuadro/nuevo-cuadro.html', context)

# REST.
class ProductoViewSet(viewsets.ModelViewSet):
        queryset = Producto.objects.all()
        serializer_class = ProductoSerializer

class ProductoFilterViewSet(generics.ListAPIView):
    serializer_class = ProductoSerializer

    def get_queryset(self):
            queryset = Producto.objects.all()
            term = self.request.query_params.get('term', None)

            if term is not None:
                    queryset = queryset.filter(descripcion__icontains = term)[:15]

            return queryset