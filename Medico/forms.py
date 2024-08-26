from django import forms
from .models import Documento,Resumen

class ResumenForm(forms.ModelForm):
    class Meta:
        model = Resumen
        fields = ['texto']
        widgets = {
            'texto': forms.Textarea()
        }
