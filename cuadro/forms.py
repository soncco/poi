# -*- coding: utf-8 -*-

from django.forms import ModelForm, TextInput
from django.forms.models import inlineformset_factory

from models import Cuadro, CuadroDetalle

class CuadroForm(ModelForm):
    class Meta:
        model = Cuadro
        fields = '__all__'

        widgets = {
            'sec_func': TextInput(attrs={
                'class': 'form-control input-sm',
                'required': 'required',
                'autocomplete': 'off',
                'placeholder': 'Sec Func'
            })
        }

class CuadroDetalleForm(ModelForm):
    class Meta:
        model = CuadroDetalle
        fields = '__all__'

CuadroDetalleFormSet = inlineformset_factory(Cuadro, CuadroDetalle, fields='__all__', form=CuadroDetalleForm)
