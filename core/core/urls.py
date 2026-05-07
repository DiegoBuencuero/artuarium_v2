from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import path, include

from promotions.views import (
    partner_list, partner_create, partner_update, partner_delete,
    promotion_create, promotion_update,
    tour_create, tour_update,
    tracking_redirect, tracking_create, tracking_delete, promociones_panel,
    sync_bokun_tours, set_featured_tour, register_redemption,
    tracking_regenerate_qr,
)
from landing.views import (
    index, reviews, correo, qr_code_view, upload_fotos, imagenes_views,
    reviews_lang, about, subscribe, subscribers_admin, test,
    qr_newsletter, qr_newsletter_code, qr_newsletter_lang,
   )

from django.conf.urls.i18n import i18n_patterns

# ---------------------------------------------------------------------------
# Rutas base (sin i18n)
# ---------------------------------------------------------------------------
urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    path("admin/", admin.site.urls),

    # URL pública del QR — corta, sin prefijo de idioma
    path("p/<str:codigo>/", tracking_redirect, name="tracking_redirect"),

    # Webhook de Bókun — fuera de i18n para evitar redirect que pierde el body
    path("api/redemption/", register_redemption, name="register_redemption"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# ---------------------------------------------------------------------------
# Rutas con i18n
# ---------------------------------------------------------------------------
urlpatterns += i18n_patterns(

    # Landing
    path("", index, name="index"),
    path("about/", about, name="about"),
    path("reviews/", reviews, name="reviews"),
    path("contact/", correo, name="contacto"),

    # Utilidades admin
    path("-admin-qr/", qr_code_view, name="qr"),
    path("upload-fotos/", upload_fotos, name="upload_fotos"),
    path("imagens/", imagenes_views, name="imagenes-views"),
    path("reviews-lang/", reviews_lang, name="reviews_lang"),
    path("subscribe/", subscribe, name="subscribe"),
    path("admin-subscribers/", subscribers_admin, name="admin_subscribers"),
    path("qr/newsletter/", qr_newsletter, name="qr_newsletter"),
    path("qr/newsletter/code/", qr_newsletter_code, name="qr_newsletter_code"),
    path("qr/newsletter/lang/", qr_newsletter_lang, name="qr_newsletter_lang"),

    # Panel de promociones
    path("admin/promociones/", promociones_panel, name="promociones"),

    # Partners
    path("promotions/partners/", partner_list, name="partner_list"),
    path("promotions/partners/create/", partner_create, name="partner_create"),
    path("promotions/partners/<int:pk>/edit/", partner_update, name="partner_update"),
    path("promotions/partners/<int:pk>/delete/", partner_delete, name="partner_delete"),

    # Promociones
    path("promotions/create/", promotion_create, name="promotion_create"),
    path("promotions/<int:pk>/edit/", promotion_update, name="promotion_update"),

    # QR / Tracking
    path("promotions/qr/", tracking_create, name="tracking_create"),
    path("promotions/qr/<int:pk>/delete/", tracking_delete, name="tracking_delete"),
    path("promotions/qr/<int:pk>/regenerate/", tracking_regenerate_qr, name="tracking_regenerate_qr"),

    # Tours
    path("dashboard/tours/", tour_create, name="tour_create"),
    path("dashboard/tours/<int:pk>/", tour_update, name="tour_update"),
    path("dashboard/tours/sync-bokun/", sync_bokun_tours, name="sync_bokun_tours"),
    path("dashboard/tours/<int:pk>/set-featured/", set_featured_tour, name="set_featured_tour"),
    # Test
    path("test/", test, name="test"),

    # Auth
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
