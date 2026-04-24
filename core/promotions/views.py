from .forms import PartnerForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Partner


def partner_list(request):
    partners = Partner.objects.all().order_by("nombre")
    return render(request, "promotions/partner_list.html", {
        "partners": partners
    })


def partner_create(request):
    if request.method == "POST":
        form = PartnerForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("partner_list")
    else:
        form = PartnerForm()  # 👈 esto te falta

    return render(request, "promotions/partner_form.html", {
        "form": form,
        "title": "Crear Partner",
    })


def partner_update(request, pk):
    partner = get_object_or_404(Partner, pk=pk)

    if request.method == "POST":
        form = PartnerForm(request.POST, instance=partner)

        if form.is_valid():
            form.save()
            return redirect("partner_list")
    else:
        form = PartnerForm(instance=partner)

    return render(request, "promotions/partner_form.html", {
        "form": form,
        "title": "Editar Partner",
    })


def partner_delete(request, pk):
    partner = get_object_or_404(Partner, pk=pk)

    if request.method == "POST":
        partner.delete()
        return redirect("/admin/promociones/#partners")

    return render(request, "promotions/partner_confirm_delete.html", {
        "partner": partner
    })