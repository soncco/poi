# -*- coding: utf-8 -*-

from django.forms import ModelForm, TextInput, DateInput, Select, Textarea, HiddenInput, NumberInput, EmailInput, DateField
from django.forms.models import inlineformset_factory

from models import Plan, Actividad

class PlanForm(ModelForm):
    class Meta:
        model = Plan
        fields = '__all__'

        labels = {
            'unidad_organica': u'Unidad orgánica',
            'accion_central': u'Acción central',
            'objetivo_especifico_institucional': u'Objetivo específico institucional',
            'periodo': u'Tipo de ejecución',
        }

        widgets = {
            'unidad_organica': Select(attrs={
                'class': 'form-control',
                'required': 'required'  
            }),
            'area_ejecutora': Select(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
            'responsable': TextInput(attrs={
                'class': 'form-control',
                'required': 'required',
                'autocomplete': 'off',
                'placeholder': 'Responsable'
            }),
            'accion_central': Textarea(attrs={
                'class': 'form-control',
                'required': 'required',
                'autocomplete': 'off',
                'placeholder': 'Acción central'
            }),
            'objetivo_general_institucional': Textarea(attrs={
                'class': 'form-control',
                'required': 'required',
                'autocomplete': 'off',
                'placeholder': 'Objetivo general institucional'
            }),
            'objetivo_especifico_institucional': Textarea(attrs={
                'class': 'form-control',
                'required': 'required',
                'autocomplete': 'off',
                'placeholder': 'Objetivo específico institucional'
            }),
            'periodo': Select(attrs={
                'class': 'form-control',
                'required': 'required',
                'autocomplete': 'off',
            }),
        }

class ActividadForm(ModelForm):
    fecha_termino = DateField(input_formats=['%d-%m-%Y'])
    class Meta:
        model = Actividad
        fields = '__all__'

ActividadFormSet = inlineformset_factory(Plan, Actividad, fields='__all__', form=ActividadForm)
