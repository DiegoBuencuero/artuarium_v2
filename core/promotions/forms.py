from django import forms
from django.forms import ModelForm

from .models import Partner, Promotion, PromotionRule, Tour, TrackingLink


class BaseForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing} form-control".strip()


class PartnerForm(BaseForm):
    class Meta:
        model = Partner
        fields = [
            "codigo", "nombre", "tipo", "activo",
            "contacto_nombre", "contacto_email", "contacto_telefono",
            "sitio_web", "direccion", "comision_default", "notas",
        ]
        widgets = {
            "notas":     forms.Textarea(attrs={"rows": 3}),
            "direccion": forms.TextInput(attrs={"placeholder": "Ej: Rua de Santa Catarina 123, Porto"}),
        }


class PromotionForm(BaseForm):
    class Meta:
        model = Promotion
        fields = [
            "nombre", "descripcion", "tipo",
            "vigencia_desde", "vigencia_hasta",
            "limite_usos", "prioridad", "estado",
        ]
        widgets = {
            "descripcion":   forms.Textarea(attrs={"rows": 3}),
            "vigencia_desde": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "vigencia_hasta": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["vigencia_desde"].input_formats = ["%Y-%m-%d"]
        self.fields["vigencia_hasta"].input_formats = ["%Y-%m-%d"]


class PromotionRuleForm(BaseForm):
    class Meta:
        model = PromotionRule
        fields = ["partner", "tour", "descuento_pct", "comision_partner_pct"]
        widgets = {
            "descuento_pct":      forms.NumberInput(attrs={"step": "0.01", "min": "0.01", "max": "100"}),
            "comision_partner_pct": forms.NumberInput(attrs={"step": "0.01", "min": "0", "max": "100"}),
        }


class TourForm(BaseForm):
    class Meta:
        model = Tour
        fields = [
            "title", "subtitle", "description", "price",
            "image", "button_text", "button_url", "bokun_widget_url", "is_active",
        ]
        widgets = {
            "description":     forms.Textarea(attrs={"rows": 4}),
            "price":           forms.NumberInput(attrs={"step": "0.01"}),
            "image":           forms.ClearableFileInput(),
            "is_active":       forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["image"].required = False



class TrackingLinkForm(forms.ModelForm):
    class Meta:
        model = TrackingLink
        fields = ['partner', 'tour', 'canal', 'notas']
        widgets = {
            'partner': forms.Select(attrs={'class': 'form-control'}),
            'tour':    forms.Select(attrs={'class': 'form-control'}),
            'canal':   forms.Select(attrs={'class': 'form-control'}),
            'notas':   forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Ej: recepción, lobby...'),
            }),
        }
        labels = {
            'partner': _('Partner'),
            'tour':    _('Tour'),
            'canal':   _('Canal'),
            'notas':   _('Notas'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mostrar TODOS los partners y tours, no solo los activos
        self.fields['partner'].queryset = Partner.objects.all().order_by('nombre')
        self.fields['tour'].queryset = Tour.objects.all().order_by('title')
        self.fields['partner'].empty_label = _("— Elegí un partner —")
        self.fields['tour'].empty_label    = _("— Elegí un tour —")