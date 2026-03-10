from django.utils import timezone
from datetime import timedelta


def reservar_estoque(pedido):

    pedido.reservado_ate = timezone.now() + timedelta(minutes=15)

    pedido.save()


def liberar_estoque(pedido):

    pedido.reservado_ate = None
    pedido.save()