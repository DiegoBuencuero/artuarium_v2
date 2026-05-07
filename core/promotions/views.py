from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.contrib import messages
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Sum

from .forms import PartnerForm, PromotionForm, PromotionRuleForm, TourForm, TrackingLinkForm
from .models import Partner, Promotion, Tour, TrackingLink


# =============================================================================
# DASHBOARD PANEL
# =============================================================================

@login_required
def promociones_panel(request):
    tipo_filtro = request.GET.get("tipo")

    partners = Partner.objects.all().order_by("nombre")
    if tipo_filtro:
        partners = partners.filter(tipo=tipo_filtro)

    context = {
        # KPIs
        "total_partners":           Partner.objects.filter(activo=True).count(),
        "total_promociones_activas": Promotion.objects.filter(estado="activa").count(),
        "total_reservas":           0,  # futuro: Redemption.objects.count()
        "comision_total":           0,  # futuro: Redemption.objects.aggregate(...)

        # Pestaña partners
        "partners":        partners,
        "tipo_filtro":     tipo_filtro,
        "tipos_partner":   Partner.TIPO_CHOICES,
        "conteo_por_tipo": Partner.objects.values("tipo").annotate(total=Count("id")),

        # Pestaña promociones
        "promociones": Promotion.objects.all().order_by("-created_at"),

        # Pestaña tours
        "tours": Tour.objects.all().order_by("-created_at"),

        # Pestaña materiales
        "tracking_links": TrackingLink.objects.select_related(
            "partner", "tour"
        ).filter(activo=True).order_by("-created_at"),
        "total_links": TrackingLink.objects.filter(activo=True).count(),

        # Resumen top partners (futuro)
        "top_partners": [],
    }

    return render(request, "promotions/dashboard-promos.html", context)


# =============================================================================
# PARTNERS
# =============================================================================

@login_required
def partner_list(request):
    partners = Partner.objects.all().order_by("nombre")
    return render(request, "promotions/partner_list.html", {"partners": partners})


@login_required
def partner_create(request):
    if request.method == "POST":
        form = PartnerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _("Partner creado correctamente"))
            return redirect("promociones")
        else:
            messages.error(request, _("Revisá los errores del formulario"))
    else:
        form = PartnerForm()

    return render(request, "promotions/partner_form.html", {
        "form": form,
        "title": _("Crear Partner"),
    })


@login_required
def partner_update(request, pk):
    partner = get_object_or_404(Partner, pk=pk)

    if request.method == "POST":
        form = PartnerForm(request.POST, instance=partner)
        if form.is_valid():
            form.save()
            messages.success(request, _("Partner actualizado correctamente"))
            return redirect("promociones")
        else:
            messages.error(request, _("Revisá los errores del formulario"))
    else:
        form = PartnerForm(instance=partner)

    return render(request, "promotions/partner_form.html", {
        "form": form,
        "title": _("Editar Partner"),
    })


@login_required
def partner_delete(request, pk):
    partner = get_object_or_404(Partner, pk=pk)

    if request.method == "POST":
        partner.delete()
        messages.success(request, _("Partner eliminado correctamente"))
        return redirect("promociones")

    return render(request, "promotions/partner_confirm_delete.html", {
        "partner": partner,
    })


# =============================================================================
# PROMOCIONES (dormidas, lógica reservada para el futuro)
# =============================================================================

@login_required
def promotion_create(request):
    promociones = Promotion.objects.all().order_by("-created_at")

    if request.method == "POST":
        promo_form = PromotionForm(request.POST)
        rule_form  = PromotionRuleForm(request.POST)

        if promo_form.is_valid() and rule_form.is_valid():
            promotion      = promo_form.save()
            rule           = rule_form.save(commit=False)
            rule.promotion = promotion
            rule.save()
            messages.success(request, _("Promoción creada correctamente"))
            return redirect("promotion_create")
        else:
            messages.error(request, _("Revisá los errores del formulario"))
    else:
        promo_form = PromotionForm()
        rule_form  = PromotionRuleForm()

    return render(request, "promotions/promotion_form.html", {
        "promo_form":  promo_form,
        "rule_form":   rule_form,
        "promociones": promociones,
    })


@login_required
def promotion_update(request, pk):
    promotion  = get_object_or_404(Promotion, pk=pk)
    rule       = promotion.rules.first()
    promociones = Promotion.objects.all().order_by("-created_at")

    if request.method == "POST":
        promo_form = PromotionForm(request.POST, instance=promotion)
        rule_form  = PromotionRuleForm(request.POST, instance=rule)

        if promo_form.is_valid() and rule_form.is_valid():
            if "borrar" in request.POST:
                promotion.delete()
                messages.success(request, _("Promoción eliminada correctamente"))
                return redirect("promotion_create")

            promotion      = promo_form.save()
            rule           = rule_form.save(commit=False)
            rule.promotion = promotion
            rule.save()
            messages.success(request, _("Promoción actualizada correctamente"))
            return redirect("promotion_create")
        else:
            messages.error(request, _("Revisá los errores del formulario"))
    else:
        promo_form = PromotionForm(instance=promotion)
        rule_form  = PromotionRuleForm(instance=rule)

    return render(request, "promotions/promotion_form.html", {
        "promo_form":  promo_form,
        "rule_form":   rule_form,
        "promociones": promociones,
        "modificacion": "S",
        "promotion":   promotion,
    })


# =============================================================================
# TOURS
# =============================================================================

@login_required
def tour_create(request):
    tours = Tour.objects.all().order_by("-created_at")

    if request.method == "POST":
        tour_form = TourForm(request.POST, request.FILES)
        if tour_form.is_valid():
            tour_form.save()
            messages.success(request, _("Tour creado correctamente"))
            return redirect("tour_create")
        else:
            messages.error(request, _("Revisá los errores del formulario"))
    else:
        tour_form = TourForm()

    return render(request, "promotions/tour_form.html", {
        "tour_form": tour_form,
        "tours":     tours,
    })


@login_required
def tour_update(request, pk):
    tour  = get_object_or_404(Tour, pk=pk)
    tours = Tour.objects.all().order_by("-created_at")

    if request.method == "POST":
        if "borrar" in request.POST:
            tour.delete()
            messages.success(request, _("Tour eliminado correctamente"))
            return redirect("tour_create")

        tour_form = TourForm(request.POST, request.FILES, instance=tour)
        if tour_form.is_valid():
            tour_form.save()
            messages.success(request, _("Tour actualizado correctamente"))
            return redirect("tour_create")
        else:
            messages.error(request, _("Revisá los errores del formulario"))
    else:
        tour_form = TourForm(instance=tour)

    return render(request, "promotions/tour_form.html", {
        "tour_form":   tour_form,
        "tours":       tours,
        "modificacion": "S",
        "tour":        tour,
    })


# =============================================================================
# TRACKING / QR
# =============================================================================

from django.db.models import F

@require_GET
def tracking_redirect(request, codigo):
    link = get_object_or_404(TrackingLink, codigo=codigo, activo=True)
    TrackingLink.objects.filter(pk=link.pk).update(clics=F('clics') + 1)

    from django.urls import reverse
    bokun_id = link.tour.bokun_id if link.tour and link.tour.bokun_id else 1
    destino = request.build_absolute_uri(reverse('index')) + f'?book={bokun_id}'

    response = redirect(destino)
    response.set_cookie(
        'artu_ref',
        codigo,
        max_age=60 * 60 * 24 * 7,
        httponly=False,
        samesite='Lax',
    )
    return response


@login_required
def tracking_create(request):
    links = TrackingLink.objects.select_related("partner", "tour").order_by("-created_at")

    if request.method == "POST":
        form = TrackingLinkForm(request.POST)
        if form.is_valid():
            link = form.save()
            try:
                base_url = request.build_absolute_uri('/').rstrip('/')
                link.generar_qr(base_url=base_url, force=True)
                messages.success(request, _("QR generado correctamente"))
            except Exception as e:
                messages.warning(request, _(f"Link creado pero el QR falló: {e}"))
            return redirect("tracking_create")
        else:
            messages.error(request, _("Revisá los errores del formulario"))
    else:
        form = TrackingLinkForm()

    return render(request, "promotions/tracking_form.html", {
        "form":  form,
        "links": links,
    })


@login_required
def tracking_delete(request, pk):
    link = get_object_or_404(TrackingLink, pk=pk)
    link.delete()
    messages.success(request, _("QR eliminado"))
    return redirect("tracking_create")


@login_required
def tracking_regenerate_qr(request, pk):
    link = get_object_or_404(TrackingLink, pk=pk)
    base_url = request.build_absolute_uri('/').rstrip('/')
    link.generar_qr(base_url=base_url, force=True)
    messages.success(request, _("QR regenerado correctamente"))
    return redirect("tracking_create")


# =============================================================================
# SYNC BÓKUN
# =============================================================================

from django.utils import timezone as tz
from . import bokun_client


@login_required
def sync_bokun_tours(request):
    if request.method != "POST":
        return redirect("tour_create")

    try:
        activities = bokun_client.get_activities()
    except Exception as e:
        messages.error(request, f"Error al conectar con Bókun: {e}")
        return redirect("tour_create")

    channel_uuid = getattr(settings, "BOKUN_CHANNEL_UUID", "")
    creados = 0
    actualizados = 0

    for act in activities:
        bokun_id_raw = act.get("id")
        if not bokun_id_raw:
            continue
        try:
            bokun_id = int(bokun_id_raw)   # Bókun devuelve el id como string
        except (ValueError, TypeError):
            continue

        # Imagen principal de Bókun
        def _extract_image(obj):
            photo = obj.get("keyPhoto") or {}
            derived = photo.get("derived", []) or []
            for d in derived:
                if d.get("name") == "large" and d.get("url"):
                    return d["url"]
            for d in derived:
                if d.get("url"):
                    return d["url"]
            url = photo.get("originalUrl") or photo.get("url")
            if url:
                return url
            # fallback: primer elemento de photos[]
            photos = obj.get("photos", []) or []
            if photos:
                return _extract_image({"keyPhoto": photos[0]})
            return None

        imagen_url = _extract_image(act)

        # Si la búsqueda no trajo imagen, pedir detalle individual
        if not imagen_url:
            try:
                detalle = bokun_client.get_activity(bokun_id)
                imagen_url = _extract_image(detalle)
            except Exception:
                pass

        precio = act.get("price")
        if precio is None:
            precio = (act.get("lowestPrice") or {}).get("amount")

        campos = {
            "title":           act.get("title", ""),
            "subtitle":        act.get("excerpt", ""),
            "description":     act.get("summary") or act.get("excerpt") or "",
            "is_active":       act.get("active", True),
            "bokun_synced_at": tz.now(),
            "duration":        act.get("durationText") or act.get("fields", {}).get("durationText", ""),
        }

        # Solo actualiza bokun_image_url si Bókun devuelve una imagen
        if imagen_url:
            campos["bokun_image_url"] = imagen_url

        if precio is not None:
            campos["price"] = precio

        if channel_uuid:
            campos["bokun_widget_url"] = (
                f"https://widgets.bokun.io/online-sales/{channel_uuid}"
                f"/experience/{bokun_id}?partialView=1"
            )

        # Crear si no existe, actualizar si ya existe
        defaults_crear = {**campos, "price": precio or 0}
        tour, created = Tour.objects.update_or_create(
            bokun_id=bokun_id,
            defaults=defaults_crear,
        )
        if created:
            creados += 1
        else:
            actualizados += 1

    partes = []
    if creados:
        partes.append(f"{creados} creado(s)")
    if actualizados:
        partes.append(f"{actualizados} actualizado(s)")

    msg = "Sync Bókun: " + ", ".join(partes) + "." if partes else "Sync completada — sin cambios."

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "message": msg})

    messages.success(request, msg)
    referer = request.META.get("HTTP_REFERER")
    return redirect(referer) if referer else redirect("promociones")


# =============================================================================
# SET FEATURED TOUR
# =============================================================================

# =============================================================================
# REGISTER REDEMPTION (llamado desde JS cuando Bókun confirma una reserva)
# =============================================================================

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Redemption

@csrf_exempt
def register_redemption(request):
    # Bókun hace GET para verificar que el endpoint existe
    if request.method == "GET":
        return JsonResponse({"ok": True, "status": "ready"})

    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "Método no permitido"}, status=405)

    # Log completo para debug — ver qué manda Bókun
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"[BOKUN WEBHOOK] body: {request.body.decode('utf-8', errors='replace')}")

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"ok": False, "error": "JSON inválido"}, status=400)

    logger.warning(f"[BOKUN WEBHOOK] parsed: {data}")

    bokun_booking_id  = str(data.get("bokun_booking_id") or data.get("bookingId") or data.get("id") or "").strip()
    bokun_activity_id = str(data.get("bokun_activity_id") or data.get("activityId") or data.get("experienceId") or "").strip()
    tracking_codigo   = str(data.get("tracking_codigo") or "").strip()

    if not bokun_booking_id:
        return JsonResponse({"ok": False, "error": "Falta booking ID"}, status=400)

    # Evitar duplicados
    if Redemption.objects.filter(bokun_booking_id=bokun_booking_id).exists():
        return JsonResponse({"ok": True, "duplicate": True})

    link = TrackingLink.objects.filter(codigo=tracking_codigo, activo=True).select_related(
        "partner", "tour", "promotion"
    ).first()

    if not link:
        return JsonResponse({"ok": False, "error": "Código de tracking no encontrado"}, status=404)

    # Si el activity_id de Bókun coincide con el tour del link, todo perfecto.
    # Si no coincide, igual registramos pero con el tour del link.
    Redemption.objects.create(
        tracking_link = link,
        partner       = link.partner,
        tour          = link.tour,
        promotion     = link.promotion,
        bokun_booking_id = bokun_booking_id,
        monto_bruto   = 0,   # se puede actualizar luego desde Bókun
        monto_neto    = 0,
        estado        = "confirmada",
        notas         = f"Registrado automáticamente. Actividad Bókun: {bokun_activity_id}",
    )

    return JsonResponse({"ok": True, "partner": link.partner.nombre, "tour": link.tour.title})


@login_required
def set_featured_tour(request, pk):
    if request.method != "POST":
        return redirect("tour_create")
    tour = get_object_or_404(Tour, pk=pk)
    tour.is_featured = True
    tour.save()          # el save() del modelo desmarca los demás
    messages.success(request, f'"{tour.title}" marcado como tour principal.')
    return redirect("tour_create")
