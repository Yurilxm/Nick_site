from django.shortcuts import redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import EmailMarketing


@require_POST
def cadastrar_email_marketing(request):
    email = request.POST.get("email")

    if not email:
        return redirect(request.META.get("HTTP_REFERER", "/"))

    obj, created = EmailMarketing.objects.get_or_create(
        email=email,
        defaults={
            "usuario": request.user if request.user.is_authenticated else None
        }
    )

    if not created and request.user.is_authenticated and not obj.usuario:
        obj.usuario = request.user
        obj.save()

    if created:
        messages.success(request, "E-mail cadastrado com sucesso! 💌")
    else:
        messages.info(request, "Esse e-mail já estava cadastrado 😉")
        
    return redirect(request.META.get("HTTP_REFERER", "/"))