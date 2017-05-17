# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test

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
