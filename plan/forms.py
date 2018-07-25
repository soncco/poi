# -*- coding: utf-8 -*-

from django.forms import ModelForm, TextInput, DateInput, Select, Textarea, HiddenInput, NumberInput, EmailInput, DateField
from django.forms.models import inlineformset_factory

from models import Plan, Actividad, Resultado

class PlanForm(ModelForm):
    class Meta:
        model = Plan
        exclude = ('numero', 'proyecto', 'area_ejecutora',)

        labels = {
            'unidad_organica': u'Unidad orgánica',
            'accion_central': u'Acción central',
            'objetivo_general_institucional': u'Objetivo general',
            'objetivo_especifico_institucional': u'Objetivo específico',
            'periodo': u'Tipo de ejecución',
            'anio': u'Año',
            'act': u'Actividad',
        }

        widgets = {
            'area_ejecutora': Select(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
            'responsable': TextInput(attrs={
                'class': 'form-control',
                'required': 'required',
                'autocomplete': 'off',
                'placeholder': ''
            }),
            'periodo': Select(attrs={
                'class': 'form-control',
                'required': 'required',
                'autocomplete': 'off',
            }),
            'act': TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'off',
                'placeholder': 'Actividad'
            }),
        }

class ActividadForm(ModelForm):
    fecha_termino = DateField(input_formats=['%d-%m-%Y'])
    class Meta:
        model = Actividad
        fields = '__all__'

ActividadFormSet = inlineformset_factory(Plan, Actividad, fields='__all__', form=ActividadForm)

class ResultadoForm(ModelForm):
    class Meta:
        model = Resultado
        fields = '__all__'
