
from django import forms
from .models import Partner

class PartnerForm(forms.ModelForm):
    class Meta:
        model = Partner
        fields = [
            "codigo", "nombre", "tipo", "activo",
            "contacto_nombre", "contacto_email", "contacto_telefono",
            "sitio_web", "direccion",
            "comision_default", "notas",
        ]
        widgets = {
            "notas": forms.Textarea(attrs={"rows": 3}),
            "direccion": forms.TextInput(attrs={"placeholder": "Ej: Rua de Santa Catarina 123, Porto"}),
        }