from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings


def enviar_email_pedido_confirmado(pedido):
    """
    Envia e-mail de confirmação quando o pedido é pago.
    """

    assunto = f"Pedido #{pedido.id} confirmado"

    destinatario = [pedido.usuario.email]

    contexto = {
        "pedido": pedido,
        "itens": pedido.itens.all(),
        "total": pedido.total,
    }

    # versão texto
    mensagem_texto = render_to_string(
        "emails/pedido_confirmado.txt",
        contexto
    )

    # versão html
    mensagem_html = render_to_string(
        "emails/pedido_confirmado.html",
        contexto
    )

    email = EmailMultiAlternatives(
        assunto,
        mensagem_texto,
        settings.DEFAULT_FROM_EMAIL,
        destinatario
    )

    email.attach_alternative(mensagem_html, "text/html")

    email.send()