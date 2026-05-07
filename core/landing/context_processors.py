from promotions.models import Tour


def featured_tour(request):
    tour = Tour.objects.filter(is_active=True, is_featured=True).first()
    return {"featured_tour": tour}
