Thanks for downloading this template!

Template Name: Gp
Template URL: https://bootstrapmade.com/gp-free-multipurpose-html-bootstrap-template/
Author: BootstrapMade.com
License: https://bootstrapmade.com/license/









from django.shortcuts import render, redirect, reverse
from django.core.mail import EmailMessage
from django.contrib import messages
from django.conf import settings
from .models import ReviewPhoto, NewsletterSubscriber
from .forms import ContactoForm,UploadFotosForm, NewsletterForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse, HttpResponse
import qrcode, io,  base64
from django.utils.translation import gettext as _
from django.core.files.base import ContentFile
from PIL import Image, ImageOps
from openpyxl import Workbook

@login_required
def login(request):
    return render (request, "login.html")

def logout(request):
   pass

def index(request):
    form = ContactoForm()
    return render(request, "index.html", {"form": form})

def about(request):
    return render(request, "about.html")

def reviews(request):
    form_fotos = UploadFotosForm()
    newsletter_form = NewsletterForm()

    return render(request, "reviews.html", {
        "upload_form": form_fotos,
        "form": newsletter_form,
        "url_name": "reviews",
    })

def correo(request):
    print("Método:", request.method)

    if request.method == 'POST':
        form = ContactoForm(request.POST)
        print("POST DATA:", request.POST.dict())

        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            correo_remitente = form.cleaned_data['correo']
            mensaje = form.cleaned_data['mensaje']
            assunto = f"Contato Site: {nombre}"

            corpo = f"""
            Você recebeu uma nova mensagem através do site.

            Nome: {nombre}
            Email: {correo_remitente}

            Mensagem:
            {mensaje}
            """

            try:
                email = EmailMessage(
                    subject=assunto,
                    body=corpo,
                    from_email=settings.EMAIL_HOST_USER,
                    to=['artur@artuarium.global'],
                    reply_to=[correo_remitente]
                )

                resultado = email.send()

                messages.success(request, "Mensagem enviada com sucesso!")

                return redirect(reverse('contacto'))

            except Exception as e:
                messages.error(request, "Erro ao enviar mensagem.")
                return redirect(reverse('contacto'))

        else:
            messages.error(request, "Por favor, verifique os campos.")
            return render(request, 'contacto.html', {'form': form})

    else:

        form = ContactoForm()
        return render(request, 'contacto.html', {'form': form})


@login_required
def qr_code_view(request):
    review_url = request.build_absolute_uri(
        reverse('reviews_lang')
    ) + f'?token={settings.REVIEW_ACCESS_TOKEN}'

    # Generar el código QR
    qr = qrcode.make(review_url)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    img_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, 'qr.html', {
        'review_url': review_url,
        'qr_image': img_base64,
    })


def reviews_lang(request):
    return render(request, "reviews-lang.html", {
        "review_token": settings.REVIEW_ACCESS_TOKEN
    })

def compress_image(file, max_width=1600, quality=80):
    img = Image.open(file)

    try:
        img = ImageOps.exif_transpose(img)
    except:
        pass

    if img.mode != "RGB":
        img = img.convert("RGB")

    w, h = img.size
    if w > max_width:
        ratio = max_width / float(w)
        img = img.resize((max_width, int(h * ratio)), Image.LANCZOS)

    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=quality)
    buffer.seek(0)
    return buffer



def upload_fotos(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "Método inválido"})

    form = UploadFotosForm(request.POST, request.FILES)

    if not form.is_valid():
        return JsonResponse({"ok": False, "error": form.errors})

    files = request.FILES.getlist("photos")

    saved = 0
    for f in files:
        compressed = compress_image(f)

        photo = ReviewPhoto()
        photo.image.save(f"{f.name}.jpg", ContentFile(compressed.read()))
        photo.save()
        saved += 1

    return JsonResponse({"ok": True, "total": saved})

@login_required
def imagenes_views(request):
    photos = ReviewPhoto.objects.all().order_by("-uploaded_at")
    return render(request, "imagenes.html", {"photos": photos})


def subscribe(request):
    if request.method == "POST":
        form = NewsletterForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Subscription successful!")
            return redirect(request.META.get("HTTP_REFERER", "index"))

        else:
            messages.error(request, "Please check the fields.")

    return redirect("index")

def subscribers_admin(request):

    if "excel" in request.GET:
        wb = Workbook()
        ws = wb.active
        ws.title = "Subscribers"

        ws.append(["Name", "Email", "Subscribed At"])

        # Datos
        for sub in NewsletterSubscriber.objects.all().order_by("-created_at"):
            ws.append([
                sub.name,
                sub.email,
                sub.created_at.strftime("%d/%m/%Y %H:%M"),
            ])

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = 'attachment; filename="subscribers.xlsx"'

        wb.save(response)
        return response

    subscribers = NewsletterSubscriber.objects.all().order_by("-created_at")
    return render(request, "admin_subscribers.html", {"subscribers": subscribers})
    
    
    
    """
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import path, include
from landing.views import index,  reviews, correo, qr_code_view, upload_fotos, imagenes_views, reviews_lang, about, subscribe, subscribers_admin
from django.conf.urls.i18n import i18n_patterns

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns(
    path("", index, name="index"),
    path("about/", about, name="about"),
    path("reviews/", reviews, name="reviews"),
    path("contact/", correo, name="contacto"),

 
    path("-admin-qr/", qr_code_view, name="qr"),
    path("upload-fotos/", upload_fotos, name="upload_fotos"),
    path("imagens/", imagenes_views, name="imagenes-views"),
    path("reviews-lang/", reviews_lang, name="reviews_lang"),
    path("subscribe/", subscribe, name="subscribe"),
    path("admin-subscribers/", subscribers_admin, name="admin_subscribers"),

    path(
        "admin-zone/",
        auth_views.LoginView.as_view(
            template_name="login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="index"),
        name="logout",
    ),
)

















