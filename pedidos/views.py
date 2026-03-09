from django.shortcuts import render, get_object_or_404
from .models import Pedido


def pedido_confirmado(request, pedido_id):

    pedido = get_object_or_404(Pedido, id=pedido_id)

    return render(request, "pedidos/pedido_confirmado.html", {"pedido": pedido}
    )