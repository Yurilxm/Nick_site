from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings



def enviar_email_pedido_confirmado(pedido):
    assunto = f"Pedido confirmado #{pedido.id} 🎉"
    destinatario = [pedido.usuario.email]

    contexto = {
        "pedido": pedido,
        "itens": pedido.itens.all(),
        "total": pedido.total_geral,
    }

    mensagem_texto = render_to_string(
        "emails/pedido_confirmado.txt",
        contexto
    )

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


def enviar_email_pedido_enviado(pedido):
    """
    Envia e-mail quando o pedido é enviado.
    """

    assunto = f"Seu pedido #{pedido.id} foi enviado 🚚"

    destinatario = [pedido.usuario.email]

    contexto = {
        "pedido": pedido,
        "itens": pedido.itens.all(),
    }

    mensagem_texto = render_to_string(
        "emails/pedido_enviado.txt",
        contexto
    )

    mensagem_html = render_to_string(
        "emails/pedido_enviado.html",
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