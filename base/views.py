# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required, user_passes_test
from plan.utils import grupo_administrador, traer_opcion, guardar_opcion

from .models import Unidad, Opcion, UnidadOrganica
from .serializers import UnidadSerializer

from rest_framework import viewsets, generics

@login_required
def index(request):
    return render(request, 'base/index.html')


def the_login(request):
    if(request.user.is_authenticated()):
        return HttpResponseRedirect(reverse('base:index'))
    else:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']

            user = authenticate(username = username, password = password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse('base:index'))
                else:
                    messages.error(request, 'El usuario no está activo.')
            else:
                messages.error(request, 'Revise el usuario o la contraseña.')

    return render(request, 'base/login.html')

def the_logout(request):
    messages.success(request, 'Hasta pronto')
    logout(request)

    return HttpResponseRedirect(reverse('base:index'))

@login_required
def my_password(request):
    user = User.objects.get(pk = request.user.pk)
    if request.method == 'POST':
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        celular = request.POST.get('celular')
        email = request.POST.get('email')

        user.first_name = first_name
        user.last_name = last_name
        user.email = email

        try:
            acceso = Acceso.objects.get(usuario = user)
            acceso.celular = celular
            acceso.save()
        except:
            print 'Admin admin'

        if password != '':
            user.set_password(password)
            user.save()
            messages.success(request, 'Se ha cambiado la contraseña correctamente.')
            return HttpResponseRedirect(reverse('base:index'))
        else:
            user.save()
            messages.success(request, 'Se han cambiado los datos del usuario.')
            return HttpResponseRedirect(reverse('base:index'))
    
    context = {'usuario': user}
    return render(request, 'base/my-password.html', context)

@login_required
@user_passes_test(grupo_administrador)
def usuarios(request):
    usuarios = User.objects.filter(id__gt = 1)
    context = {'usuarios': usuarios}
    return render(request, 'base/usuarios.html', context)

@login_required
@user_passes_test(grupo_administrador)
def usuario(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        is_active = request.POST.get('is_active')
        grupos = request.POST.getlist('grupos[]')

        try:
            user = User.objects.create_user(username, '', password)
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.is_active = True if is_active == '1' else False

            user.save()

            for grupo in grupos:
                the_grupo = Group.objects.get(pk = grupo)
                user.groups.add(the_grupo)
                if the_grupo.pk == 1 or the_grupo.pk == 2:
                    user.is_staff = True
                user.save()

            messages.success(request, 'Se han guardado los datos del nuevo usuario.')
            return HttpResponseRedirect(reverse('base:usuarios'))
        except Exception, e:
            print str(e)
            messages.error(request, 'Ya existe un usuario con el mismo nombre.')
        

    grupos = Group.objects.all()

    context = {'grupos': grupos}
    return render(request, 'base/usuario.html', context)

@login_required
@user_passes_test(grupo_administrador)
def usuario_editar(request, id):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        is_active = request.POST.get('is_active')
        grupos = request.POST.getlist('grupos[]')

        user = User.objects.get(pk = id)

        try:
            user.username = username
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.is_active = True if is_active == '1' else False
            user.save()

            if password != '':
                user.set_password(password)
                user.save()

            user.groups.clear()

            for grupo in grupos:
                the_grupo = Group.objects.get(pk = grupo)
                user.groups.add(the_grupo)
                if the_grupo.pk == 1 or the_grupo.pk == 2:
                    user.is_staff = True
                user.save()

            messages.success(request, 'Se han cambiado los datos del usuario.')
            return HttpResponseRedirect(reverse('base:usuarios'))

        except Exception, e:
            messages.error(request, 'Ya existe un usuario con el mismo nombre.')

    if id == '1':
        raise Http404
    usuario = User.objects.get(pk = id)

    grupos = Group.objects.all()

    context = {'grupos': grupos, 'usuario': usuario}
    return render(request, 'base/usuario-editar.html', context)

# REST.
class UnidadViewSet(viewsets.ModelViewSet):
    queryset = Unidad.objects.all()
    serializer_class = UnidadSerializer

class UnidadFilterViewSet(generics.ListAPIView):
    serializer_class = UnidadSerializer

    def get_queryset(self):
        queryset = Unidad.objects.all()
        organica = self.request.query_params.get('organica', None)

        if organica is not None:
            queryset = queryset.filter(pertenece_a__pk = organica)

        return queryset


def handler404(request):
    response = render(request, 'base/404.html', {})
    response.status_code = 403
    return response

def handler403(request):
    response = render(request, 'base/403.html', {})
    response.status_code = 403
    return response

import sys
def handler500(request):
    type_, value, traceback = sys.exc_info()
    response = render(request, 'base/500.html', {'value_': value})
    response.status_code = 500
    return response

@login_required
@user_passes_test(grupo_administrador)
def opciones(request):

    if request.method == 'POST':
        mostrar_mensaje = request.POST.get('mostrar_mensaje')
        mensaje = request.POST.get('mensaje')

        guardar_opcion('mostrar_mensaje', mostrar_mensaje)
        guardar_opcion('mensaje', mensaje)

        messages.success(request, 'Se han guardado las opciones.')
        return HttpResponseRedirect(reverse('base:opciones'))
    

    mostrar_mensaje = traer_opcion('mostrar_mensaje')
    mensaje = traer_opcion('mensaje')

    context = {'mostrar_mensaje': mostrar_mensaje, 'mensaje': mensaje}
    return render(request, 'base/opciones.html', context)


@login_required
@user_passes_test(grupo_administrador)
def alineacion(request):
    organicas = UnidadOrganica.objects.all()
    context = {'organicas': organicas}
    return render(request, 'base/alineacion.html', context)
