# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, user_passes_test

from .models import Cuadro, CuadroDetalle, Producto, Clasificador
from .forms import CuadroForm, CuadroDetalleFormSet
from .serializers import ProductoSerializer, ClasificadorSerializer
from plan.models import Actividad

from rest_framework import viewsets, generics

from base.models import UnidadOrganica, Unidad

from plan.utils import grupo_logistico, grupo_administrador
from plan.mail import notificar_cuadro

from .utils import modificar_post


import json, datetime

@login_required
def nuevo_cuadro(request, id):
    actividad = Actividad.objects.get(pk = id)
    if request.method == 'POST':
        nuevo_post = modificar_post(request.POST, CuadroDetalleFormSet().prefix)
        form = CuadroForm(nuevo_post)
        detalle_form = CuadroDetalleFormSet(nuevo_post)
        pass

        if form.is_valid() and detalle_form.is_valid():
            cuadro = form.save(commit=False)
            cuadro.actividad = actividad

            cuadro.save()
            detalle_form.instance = cuadro
            detalle_form.save()

            if request.POST.get('pre') == 'no':
                messages.success(request, 'Se ha creado un cuadro de necesidades.')
                #notificar_cuadro(cuadro)
                return HttpResponseRedirect(reverse('plan:actividades', args=[actividad.pertenece_a.pk]))
            else:
                messages.success(request, 'Se ha preguardado el cuadro de necesidades.')
                return HttpResponseRedirect(reverse('cuadro:editar_cuadro', args=[actividad.pk]))

        else:
            print form.errors
            print detalle_form.errors
    form = CuadroForm()
    detalle_form = CuadroDetalleFormSet()
    context = {'actividad': actividad, 'form': form, 'detalle_form': detalle_form}
    return render(request, 'cuadro/nuevo-cuadro.html', context)

@login_required
def editar_cuadro(request, id):
    actividad = Actividad.objects.get(pk = id)
    cuadro = actividad.cuadro
    if request.method == 'POST':
        nuevo_post = modificar_post(request.POST, CuadroDetalleFormSet().prefix)
        form = CuadroForm(nuevo_post, instance = cuadro)

        if form.is_valid():
            cuadro = form.save(commit=False)
            detalle_form = CuadroDetalleFormSet(nuevo_post, instance=cuadro)
            if detalle_form.is_valid():
                cuadro.save()
                for detalle in cuadro.cuadrodetalle_set.all():
                    detalle.delete()
                detalle_form.save()

                if request.POST.get('pre') == 'no':
                    messages.success(request, 'Se ha editado el cuadro de necesidades.')
                    return HttpResponseRedirect(reverse('plan:actividades', args=[actividad.pertenece_a.pk]))
                else:
                    messages.success(request, 'Se ha preguardado el cuadro de necesidades.')
                    return HttpResponseRedirect(reverse('cuadro:editar_cuadro', args=[actividad.pk]))

            else:
                print detalle_form.errors
        else:
            print detalle_form.errors


    form = CuadroForm(instance=cuadro)
    detalle_form = CuadroDetalleFormSet()
    context = {'actividad': actividad, 'form': form, 'detalle_form': detalle_form, 'cuadro': cuadro}
    return render(request, 'cuadro/editar-cuadro.html', context)

@login_required
def borrar_cuadro(request, id):
    actividad = Actividad.objects.get(pk = id)
    cuadro = actividad.cuadro
    cuadro.delete()
    messages.success(request, 'Se ha borrado el cuadro de necesidades.')
    return HttpResponseRedirect(reverse('plan:actividades', args=[actividad.pertenece_a.pk]))

# Informes
@login_required
def informe_dependencia(request):
    unidades = Unidad.objects.all()
    context = {'unidades': unidades}
    return render(request, 'cuadro/informe-dependencia.html', context)

@login_required
def informe_organica(request):
    unidades = UnidadOrganica.objects.all()
    context = {'unidades': unidades}
    return render(request, 'cuadro/informe-organica.html', context)

@login_required
def informe_institucion(request):
    context = {}
    return render(request, 'cuadro/informe-institucion.html', context)



# REST.
class ProductoViewSet(viewsets.ModelViewSet):
        queryset = Producto.objects.all()
        serializer_class = ProductoSerializer

class ClasificadorViewSet(viewsets.ModelViewSet):
        queryset = Clasificador.objects.all()
        serializer_class = ClasificadorSerializer

class ProductoFilterViewSet(generics.ListAPIView):
    serializer_class = ProductoSerializer

    def get_queryset(self):
            queryset = Producto.objects.all()
            term = self.request.query_params.get('term', None)

            if term is not None:
                    queryset = queryset.filter(descripcion__istartswith = term)[:15]

            return queryset

class ClasificadorFilterViewSet(generics.ListAPIView):
        serializer_class = ClasificadorSerializer

        def get_queryset(self):
                queryset = Clasificador.objects.all()
                term = self.request.query_params.get('term', None)

                if term is not None:
                        queryset = queryset.filter(cadena__icontains = term) | queryset.filter(descripcion__icontains = term)

                return queryset[:10]
