"""
promotions/models.py

Sistema de promociones para partners (hoteles, restaurantes, tiendas, etc.).
Integrado con la app `landing` (Tour).
"""

import io
import secrets
import string
from decimal import Decimal
from django.core.files.base import ContentFile
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


# =============================================================================
# CAPA 1 — CATÁLOGO
# =============================================================================

class Partner(models.Model):
    """
    Socio comercial que distribuye promociones (hoteles, restaurantes,
    tiendas, bloggers, agencias, etc.).
    """

    TIPO_CHOICES = [
        ("hotel",       "Hotel"),
        ("apartamento", "Apartamento turístico"),
        ("restaurante", "Restaurante"),
        ("bar",         "Bar / Café"),
        ("tienda",      "Tienda / Souvenir"),
        ("concierge",   "Concierge / Guía"),
        ("agencia",     "Agencia de viajes"),
        ("blogger",     "Blogger / Influencer"),
        ("evento",      "Evento / Festival"),
        ("otro",        "Otro"),
    ]

    codigo = models.CharField(
        "Código",
        max_length=20,
        unique=True,
        help_text="Identificador corto único, ej: HTL001, REST005, BLG002",
    )
    nombre = models.CharField("Nombre", max_length=200)
    tipo = models.CharField("Tipo", max_length=20, choices=TIPO_CHOICES, default="hotel")

    contacto_nombre = models.CharField("Contacto", max_length=150, blank=True)
    contacto_email = models.EmailField("Email de contacto", blank=True)
    contacto_telefono = models.CharField("Teléfono", max_length=50, blank=True)
    sitio_web = models.URLField("Sitio web", blank=True)
    direccion = models.CharField("Dirección", max_length=255, blank=True)
    notas = models.TextField("Notas internas", blank=True)

    comision_default = models.DecimalField(
        "Comisión por defecto (%)",
        max_digits=5, decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Comisión que recibe el partner por reserva. Puede sobrescribirse por promoción.",
    )

    activo = models.BooleanField("Activo", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Partner"
        verbose_name_plural = "Partners"
        ordering = ["nombre"]
        indexes = [
            models.Index(fields=["tipo", "activo"]),
        ]

    def __str__(self):
        return f"{self.codigo} — {self.nombre} ({self.get_tipo_display()})"


# =============================================================================
# CAPA 2 — PROMOCIONES (núcleo flexible)
# =============================================================================

class Promotion(models.Model):
    """
    Contenedor de promoción. Su comportamiento concreto se define en PromotionRule.
    """

    TIPO_CHOICES = [
        ("partner_tour", "Partner + Tour específico"),
        ("partner_all",  "Partner + Todos los tours"),
        ("tour_all",     "Tour + Todos los partners"),
        ("global",       "Promoción global"),
    ]

    ESTADO_CHOICES = [
        ("borrador", "Borrador"),
        ("activa",   "Activa"),
        ("pausada",  "Pausada"),
        ("vencida",  "Vencida"),
    ]

    nombre = models.CharField("Nombre interno", max_length=200)
    descripcion = models.TextField("Descripción", blank=True)
    tipo = models.CharField("Tipo", max_length=20, choices=TIPO_CHOICES)

    vigencia_desde = models.DateField("Vigente desde")
    vigencia_hasta = models.DateField("Vigente hasta", null=True, blank=True)

    limite_usos = models.PositiveIntegerField(
        "Límite de usos", null=True, blank=True,
        help_text="Dejar vacío para uso ilimitado.",
    )
    usos_actuales = models.PositiveIntegerField("Usos actuales", default=0)

    prioridad = models.PositiveSmallIntegerField(
        "Prioridad", default=10,
        help_text="Mayor número = mayor prioridad cuando varias promos califican.",
    )

    estado = models.CharField("Estado", max_length=20, choices=ESTADO_CHOICES, default="borrador")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Promoción"
        verbose_name_plural = "Promociones"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.nombre} ({self.get_estado_display()})"

    def esta_vigente(self):
        hoy = timezone.now().date()
        if self.estado != "activa":
            return False
        if hoy < self.vigencia_desde:
            return False
        if self.vigencia_hasta and hoy > self.vigencia_hasta:
            return False
        if self.limite_usos and self.usos_actuales >= self.limite_usos:
            return False
        return True


class PromotionRule(models.Model):
    """
    Regla concreta dentro de una promoción.
    partner y tour son opcionales (null = 'todos').
    """

    promotion = models.ForeignKey(
        Promotion, related_name="rules",
        on_delete=models.CASCADE,
    )
    partner = models.ForeignKey(
        Partner, related_name="promotion_rules",
        null=True, blank=True,
        on_delete=models.CASCADE,
        help_text="Vacío = aplica a todos los partners.",
    )
    tour = models.ForeignKey(
        "landing.Tour",
        related_name="promotion_rules",
        null=True, blank=True,
        on_delete=models.CASCADE,
        help_text="Vacío = aplica a todos los tours.",
    )

    descuento_pct = models.DecimalField(
        "Descuento (%)",
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01")), MaxValueValidator(Decimal("100"))],
    )

    comision_partner_pct = models.DecimalField(
        "Comisión partner (%)",
        max_digits=5, decimal_places=2,
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Si vacío, usa la comisión por defecto del partner.",
    )

    class Meta:
        verbose_name = "Regla de promoción"
        verbose_name_plural = "Reglas de promoción"
        constraints = [
            models.UniqueConstraint(
                fields=["promotion", "partner", "tour"],
                name="unique_rule_per_promotion",
            ),
        ]

    def __str__(self):
        p = self.partner.codigo if self.partner else "TODOS"
        t = self.tour.title if self.tour else "TODOS"
        return f"{p} × {t} → {self.descuento_pct}%"


# =============================================================================
# TRACKING (canales de distribución)
# =============================================================================

def _generar_slug_unico(largo=10):
    alfabeto = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alfabeto) for _ in range(largo))


class TrackingLink(models.Model):
    """
    Link único por canal asociado a una promoción + partner.
    """

    CANAL_CHOICES = [
        ("qr",       "QR físico"),
        ("web_link", "Link web"),
        ("widget",   "Widget embebido"),
    ]

    promotion = models.ForeignKey(
        Promotion, related_name="tracking_links",
        on_delete=models.CASCADE,
    )
    partner = models.ForeignKey(
        Partner, related_name="tracking_links",
        on_delete=models.CASCADE,
        help_text="Partner concreto al que se entregó este material.",
    )
    canal = models.CharField("Canal", max_length=20, choices=CANAL_CHOICES)
    codigo = models.CharField(
        "Código URL", max_length=20, unique=True,
        help_text="Slug que aparece en la URL pública.",
    )

    qr_image = models.ImageField("Imagen QR", upload_to="promotions/qr/", blank=True, null=True)
    notas = models.CharField("Notas internas", max_length=255, blank=True)

    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Link de tracking"
        verbose_name_plural = "Links de tracking"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.codigo:
            while True:
                slug = _generar_slug_unico()
                if not TrackingLink.objects.filter(codigo=slug).exists():
                    self.codigo = slug
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.partner.codigo} · {self.get_canal_display()} · {self.codigo}"

    def url_publica(self, base_url=""):
        return f"{base_url}/p/{self.codigo}"

    def generar_qr(self, base_url=None, force=False):
        """Genera y guarda la imagen QR para este tracking link."""
        import qrcode
        from django.conf import settings

        if self.qr_image and not force:
            return self.qr_image.url

        base = base_url or getattr(settings, "SITE_BASE_URL", "")
        url = self.url_publica(base_url=base)

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")

        filename = f"qr_{self.codigo}.png"
        self.qr_image.save(filename, ContentFile(buffer.getvalue()), save=True)
        return self.qr_image.url


# =============================================================================
# CAPA 3 — ATRIBUCIÓN Y CONVERSIÓN
# =============================================================================

class Redemption(models.Model):
    """
    Registro contable de cada reserva concretada vía una promoción.
    Guarda SNAPSHOT de partner/tour/descuento para reportes históricos.
    """

    ESTADO_CHOICES = [
        ("pendiente",  "Pendiente de pago a partner"),
        ("confirmada", "Reserva confirmada"),
        ("pagada",     "Comisión pagada"),
        ("cancelada",  "Cancelada"),
    ]

    tracking_link = models.ForeignKey(
        TrackingLink, related_name="redemptions",
        on_delete=models.PROTECT,
    )

    promotion = models.ForeignKey(
        Promotion, related_name="redemptions",
        on_delete=models.PROTECT,
    )
    partner = models.ForeignKey(
        Partner, related_name="redemptions",
        on_delete=models.PROTECT,
    )
    tour = models.ForeignKey(
        "landing.Tour", related_name="redemptions",
        on_delete=models.PROTECT,
    )

    bokun_booking_id = models.CharField(
        "ID reserva Bókun", max_length=100,
        unique=True, db_index=True,
    )

    monto_bruto = models.DecimalField("Monto bruto", max_digits=10, decimal_places=2)
    descuento_pct_aplicado = models.DecimalField("Descuento aplicado (%)", max_digits=5, decimal_places=2)
    descuento_monto = models.DecimalField("Monto descontado", max_digits=10, decimal_places=2)
    monto_neto = models.DecimalField("Monto neto cobrado", max_digits=10, decimal_places=2)

    comision_partner_pct = models.DecimalField("Comisión partner (%)", max_digits=5, decimal_places=2)
    comision_partner_monto = models.DecimalField("Comisión partner ($)", max_digits=10, decimal_places=2)

    cliente_nombre = models.CharField(max_length=200, blank=True)
    cliente_email = models.EmailField(blank=True)

    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="confirmada")
    notas = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    pagada_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Redención"
        verbose_name_plural = "Redenciones"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["partner", "created_at"]),
            models.Index(fields=["tour", "created_at"]),
            models.Index(fields=["estado"]),
        ]

    def __str__(self):
        return f"{self.partner.codigo} · {self.tour.title} · ${self.monto_neto}"
