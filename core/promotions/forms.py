from django import forms
from django.forms import ModelForm

from .models import Partner, PromotionRule, Promotion


class BaseForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            existing_class = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing_class} form-control".strip()


class BaseSimpleForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(BaseSimpleForm, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            existing_class = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing_class} form-control".strip()


class PartnerForm(BaseForm):
    class Meta:
        model = Partner
        fields = [
            "codigo",
            "nombre",
            "tipo",
            "activo",
            "contacto_nombre",
            "contacto_email",
            "contacto_telefono",
            "sitio_web",
            "direccion",
            "comision_default",
            "notas",
        ]
        widgets = {
            "notas": forms.Textarea(attrs={"rows": 3}),
            "direccion": forms.TextInput(
                attrs={
                    "placeholder": "Ej: Rua de Santa Catarina 123, Porto",
                }
            ),
        }


class PromotionForm(BaseForm):
    class Meta:
        model = Promotion
        fields = [
            "nombre",
            "descripcion",
            "tipo",
            "vigencia_desde",
            "vigencia_hasta",
            "limite_usos",
            "prioridad",
            "estado",
        ]
        widgets = {
            "descripcion": forms.Textarea(
                attrs={
                    "rows": 3,
                }
            ),
            "vigencia_desde": forms.DateInput(
                attrs={
                    "type": "date",
                },
                format="%Y-%m-%d",
            ),
            "vigencia_hasta": forms.DateInput(
                attrs={
                    "type": "date",
                },
                format="%Y-%m-%d",
            ),
        }

    def __init__(self, *args, **kwargs):
        super(PromotionForm, self).__init__(*args, **kwargs)

        self.fields["vigencia_desde"].input_formats = ["%Y-%m-%d"]
        self.fields["vigencia_hasta"].input_formats = ["%Y-%m-%d"]


class PromotionRuleForm(BaseForm):
    class Meta:
        model = PromotionRule
        fields = [
            "partner",
            "tour",
            "descuento_pct",
            "comision_partner_pct",
        ]
        widgets = {
            "descuento_pct": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "min": "0.01",
                    "max": "100",
                }
            ),
            "comision_partner_pct": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "min": "0",
                    "max": "100",
                }
            ),
        }