from django.conf import settings

def social_links(request):
    return {
        "SOCIAL_LINKS": settings.SOCIAL_LINKS
    }