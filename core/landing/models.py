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
    

