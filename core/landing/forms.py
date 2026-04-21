from django import forms
from .models import NewsletterSubscriber
from django.forms import ModelForm, Form
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import AuthenticationForm


class BaseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            css = f.widget.attrs.get("class", "")
            f.widget.attrs["class"] = (css + " form-control").strip()


class ContactoForm(forms.Form):
    nombre = forms.CharField(
        max_length=100,
        label=_("Name"),
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "placeholder": _("Your Name"),
        }),
    )

    correo = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={
            "class": "form-input",
            "placeholder": _("Your Email"),
        }),
    )

    mensaje = forms.CharField(
        label=_("Message"),
        widget=forms.Textarea(attrs={
            "class": "form-input",
            "placeholder": _("Your Message"),
            "rows": 4,
        }),
    )

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Usuário ou e-mail',
            'class': 'form-control'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Senha',
            'class': 'form-control'
        })
    )

class UploadFotosForm(forms.Form):

    photos = forms.FileField(required=True)

    def clean(self):
        cleaned = super().clean()
        files = self.files.getlist("photos")

        if not files:
            raise forms.ValidationError("Nenhuma foto enviada.")

        for f in files:
            if f.size > 8 * 1024 * 1024:
                raise forms.ValidationError("Cada foto deve ter menos de 8MB.")

            if not f.content_type.startswith("image/"):
                raise forms.ValidationError("Envie apenas imagens.")

        cleaned["photos"] = files
        return cleaned

class NewsletterForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ['name', 'email']

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Your name"
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': "Your best email"
            }),
        }