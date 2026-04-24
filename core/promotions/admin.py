# promotions/admin.py

from django.contrib import admin
from .models import Partner, Promotion, PromotionRule, TrackingLink, Redemption
from landing.models import Tour


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    search_fields = ("title",)


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "tipo", "activo")
    search_fields = ("codigo", "nombre")
    list_filter = ("tipo", "activo")


class PromotionRuleInline(admin.TabularInline):
    model = PromotionRule
    autocomplete_fields = ("partner", "tour")
    extra = 1


class TrackingLinkInline(admin.TabularInline):
    model = TrackingLink
    autocomplete_fields = ("partner",)
    readonly_fields = ("codigo",)
    extra = 0


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo", "estado", "vigencia_desde")
    list_filter = ("estado", "tipo")
    search_fields = ("nombre", "descripcion")  
    inlines = [PromotionRuleInline, TrackingLinkInline]


@admin.register(PromotionRule)
class PromotionRuleAdmin(admin.ModelAdmin):
    list_display = ("promotion", "partner", "tour", "descuento_pct")
    autocomplete_fields = ("promotion", "partner", "tour")


@admin.register(TrackingLink)
class TrackingLinkAdmin(admin.ModelAdmin):
    list_display = ("codigo", "promotion", "partner", "canal", "activo")
    autocomplete_fields = ("promotion", "partner")
    search_fields = ("codigo",)


@admin.register(Redemption)
class RedemptionAdmin(admin.ModelAdmin):
    list_display = ("created_at", "partner", "tour", "monto_neto", "estado")
    list_filter = ("estado", "partner")