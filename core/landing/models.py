from django.db import models

class ReviewPhoto(models.Model):
    token = models.CharField(max_length=100)
    image = models.ImageField(upload_to="reviews/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.token} — {self.image.name}"
    
class Reputaciones(models.Model):
    nombre = models.CharField("Nombre del cliente", max_length=150)
    texto = models.TextField("Comentario")
    rating = models.PositiveSmallIntegerField("Estrellas", choices=[(i, f"{i} ★") for i in range(1, 6)])
    origen = models.CharField("Origen", max_length=50, blank=True)
    publicar = models.BooleanField("¿Publicar en el sitio?", default=False)

    class Meta:
        verbose_name = "Reputación"
        verbose_name_plural = "Reputaciones"
        ordering = ["-id"]

    def __str__(self):
        return f"{self.nombre} - {self.rating}★"

class NewsletterSubscriber(models.Model):
    name = models.CharField(max_length=120, null=True, blank=True)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"
    

from django.db import models

class Tour(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='tours/')
    button_text = models.CharField(max_length=100, default='VER JORNADA')
    button_url = models.URLField(blank=True, null=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title