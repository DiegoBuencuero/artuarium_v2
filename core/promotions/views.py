from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from .forms import PartnerForm, PromotionRuleForm, PromotionForm
from .models import Partner, Promotion


@login_required
def partner_list(request):
    partners = Partner.objects.all().order_by("nombre")
    return render(request, "promotions/partner_list.html", {
        "partners": partners,
    })


@login_required
def partner_create(request):
    if request.method == "POST":
        form = PartnerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("promociones")
    else:
        form = PartnerForm()

    return render(request, "promotions/partner_form.html", {
        "form": form,
        "title": "Crear Partner",
    })


@login_required
def partner_update(request, pk):
    partner = get_object_or_404(Partner, pk=pk)

    if request.method == "POST":
        form = PartnerForm(request.POST, instance=partner)
        if form.is_valid():
            form.save()
            return redirect("promociones")
    else:
        form = PartnerForm(instance=partner)

    return render(request, "promotions/partner_form.html", {
        "form": form,
        "title": "Editar Partner",
    })


@login_required
def partner_delete(request, pk):
    partner = get_object_or_404(Partner, pk=pk)

    if request.method == "POST":
        partner.delete()
        return redirect("promociones")

    return render(request, "promotions/partner_confirm_delete.html", {
        "partner": partner,
    })



@login_required
def promotion_create(request):
    promociones = Promotion.objects.all().order_by("-created_at")

    if request.method == "POST":
        promo_form = PromotionForm(request.POST)
        rule_form = PromotionRuleForm(request.POST)

        if promo_form.is_valid() and rule_form.is_valid():
            promotion = promo_form.save()

            rule = rule_form.save(commit=False)
            rule.promotion = promotion
            rule.save()

            messages.success(request, _("Promoción creada correctamente"))
            return redirect("promotion_create")
        else:
            messages.error(request, _("Revisá los errores del formulario"))
    else:
        promo_form = PromotionForm()
        rule_form = PromotionRuleForm()

    return render(request, "promotions/promotion_form.html", {
        "promo_form": promo_form,
        "rule_form": rule_form,
        "promociones": promociones,
    })


@login_required
def promotion_update(request, pk):
    promotion = get_object_or_404(Promotion, pk=pk)
    rule = promotion.rules.first()
    promociones = Promotion.objects.all().order_by("-created_at")

    if request.method == "POST":
        promo_form = PromotionForm(request.POST, instance=promotion)
        rule_form = PromotionRuleForm(request.POST, instance=rule)

        if promo_form.is_valid() and rule_form.is_valid():
            if "borrar" in request.POST:
                promotion.delete()
                messages.success(request, _("Promoción eliminada correctamente"))
                return redirect("promotion_create")

            promotion = promo_form.save()

            rule = rule_form.save(commit=False)
            rule.promotion = promotion
            rule.save()

            messages.success(request, _("Promoción actualizada correctamente"))
            return redirect("promotion_create")
        else:
            messages.error(request, _("Revisá los errores del formulario"))
    else:
        promo_form = PromotionForm(instance=promotion)
        rule_form = PromotionRuleForm(instance=rule)

    return render(request, "promotions/promotion_form.html", {
        "promo_form": promo_form,
        "rule_form": rule_form,
        "promociones": promociones,
        "modificacion": "S",
        "promotion": promotion,
    })