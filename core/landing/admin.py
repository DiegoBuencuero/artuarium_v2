from django.contrib import admin
from .models import ReviewPhoto, NewsletterSubscriber

@admin.register(ReviewPhoto)
class ReviewPhotoAdmin(admin.ModelAdmin):
    list_display = ("token", "preview", "uploaded_at")
    readonly_fields = ("preview",)

    def preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="80" style="border-radius:4px;" />'
        return "—"
    preview.allow_tags = True
    preview.short_description = "Preview"


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created_at")
    search_fields = ("name", "email")
    list_filter = ("created_at",)
    ordering = ("-created_at",)
