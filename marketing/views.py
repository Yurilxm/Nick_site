from django.shortcuts import redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils.http import url_has_allowed_host_and_scheme
from .models import EmailMarketing


def _referer_seguro(request):
    referer = request.META.get("HTTP_REFERER", "/")
    if url_has_allowed_host_and_scheme(url=referer, allowed_hosts={request.get_host()}):
        return referer
    return "/"


@require_POST
def cadastrar_email_marketing(request):
    email = request.POST.get("email")

    if not email:
        return redirect(_referer_seguro(request))

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

    return redirect(_referer_seguro(request))