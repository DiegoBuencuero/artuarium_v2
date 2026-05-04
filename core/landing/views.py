from django.shortcuts import render, redirect, reverse
from django.core.mail import EmailMessage
from django.contrib import messages
from django.conf import settings
from .models import ReviewPhoto, NewsletterSubscriber
from promotions.models import Tour
from .forms import ContactoForm,UploadFotosForm, NewsletterForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse, HttpResponse
import qrcode, io,  base64
from django.utils.translation import gettext as _
from django.core.files.base import ContentFile
from PIL import Image, ImageOps
from openpyxl import Workbook


def login(request):
    return render (request, "login.html")


def logout(request):
   pass

# def index(request):
#     form = ContactoForm()
#     return render(request, "index.html", {"form": form})

def index(request):
    form = ContactoForm()
    active_tours = Tour.objects.filter(is_active=True)
    featured_tour = active_tours.filter(is_featured=True).first()
    other_tours = active_tours.filter(is_featured=False)

    return render(request, "index2.html", {
        "form": form,
        "tours": active_tours,
        "featured_tour": featured_tour,
        "other_tours": other_tours,
    })

def about(request):
    return render(request, "about.html")

@login_required
def test(request):
    return render(request, "test.html")

def reviews(request):
    form_fotos = UploadFotosForm()
    newsletter_form = NewsletterForm()

    return render(request, "reviews.html", {
        "upload_form": form_fotos,
        "form": newsletter_form,
        "url_name": "reviews",
    })

def qr_newsletter(request):
    form = NewsletterForm()
    return render(request, "qr_newsletter.html", {
        "form": form
    })

def qr_newsletter_code(request):
    newsletter_url = request.build_absolute_uri(
        reverse('qr_newsletter_lang')
    )
    qr = qrcode.make(newsletter_url)

    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    img_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, 'qr_newsletter_code.html', {
        'qr_image': img_base64,
        'newsletter_url': newsletter_url
    })

def qr_newsletter_lang(request):
    return render(request, 'qr_newsletter_lang.html')

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

@login_required
def reviews_lang(request):
    return render(request, "reviews-lang.html", {
        "review_token": settings.REVIEW_ACCESS_TOKEN
    })

@login_required
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

@login_required
def subscribe(request):
    if request.method == "POST":
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()

            messages.success(
                request,
                _("Obrigado por se inscrever na newsletter.")
            )

            return redirect(request.META.get("HTTP_REFERER", "/"))
    return redirect("index")

@login_required
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

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum, Count
from promotions.models import Partner, Promotion, TrackingLink, Redemption

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum, Count
from promotions.models import Partner, Promotion, TrackingLink, Redemption


@login_required
def promociones_panel(request):
    """Panel principal de gestión de promociones para partners."""

    # Filtro opcional por tipo de partner
    tipo_filtro = request.GET.get("tipo", "")

    partners_qs = Partner.objects.all()
    if tipo_filtro:
        partners_qs = partners_qs.filter(tipo=tipo_filtro)

    # Indicadores generales
    total_partners = Partner.objects.filter(activo=True).count()
    total_promociones_activas = Promotion.objects.filter(estado="activa").count()
    total_links = TrackingLink.objects.filter(activo=True).count()

    # Stats de redenciones
    redemptions_qs = Redemption.objects.filter(estado__in=["confirmada", "pagada"])
    total_reservas = redemptions_qs.count()
    monto_total = redemptions_qs.aggregate(total=Sum("monto_neto"))["total"] or 0
    comision_total = redemptions_qs.aggregate(total=Sum("comision_partner_monto"))["total"] or 0

    # Top partners por reservas
    top_partners = (
        Partner.objects
        .annotate(
            reservas=Count("redemptions"),
            ingreso=Sum("redemptions__monto_neto"),
        )
        .filter(reservas__gt=0)
        .order_by("-reservas")[:5]
    )

    # Conteo por tipo (para badges/filtros)
    conteo_por_tipo = (
        Partner.objects.values("tipo")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    context = {
        "url_name": "promociones",
        "total_partners": total_partners,
        "total_promociones_activas": total_promociones_activas,
        "total_links": total_links,
        "total_reservas": total_reservas,
        "monto_total": monto_total,
        "comision_total": comision_total,
        "top_partners": top_partners,
        "conteo_por_tipo": conteo_por_tipo,
        "tipo_filtro": tipo_filtro,
        "partners": partners_qs.order_by("nombre"),
        "promociones": Promotion.objects.all().order_by("-created_at")[:20],
        "tours": Tour.objects.all().order_by("-created_at"),
        "tracking_links": TrackingLink.objects.select_related("partner", "tour").filter(activo=True).order_by("-created_at")[:20],
        "tipos_partner": Partner.TIPO_CHOICES,
    }
    return render(request, "promotions/dashboard-promos.html", context)