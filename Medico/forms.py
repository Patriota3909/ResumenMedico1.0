from django import forms
from .models import Documento,Resumen
from froala_editor.widgets import FroalaEditor

class ResumenForm(forms.ModelForm):
    class Meta:
        model = Resumen
        fields = ['texto']
        widgets = {
            'texto': FroalaEditor(),
        }
