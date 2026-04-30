from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.contrib import messages
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

@require_GET
def tracking_redirect(request, codigo):
    link = get_object_or_404(TrackingLink, codigo=codigo, activo=True)
    TrackingLink.objects.filter(pk=link.pk).update(clics=link.clics + 1)
    destino = link.tour.bokun_widget_url or link.tour.button_url or "/"
    return redirect(destino)


@login_required
def tracking_create(request):
    links = TrackingLink.objects.select_related("partner", "tour").order_by("-created_at")

    if request.method == "POST":
        form = TrackingLinkForm(request.POST)
        if form.is_valid():
            link = form.save()
            try:
                link.generar_qr()
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
