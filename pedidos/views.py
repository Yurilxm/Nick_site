from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from carrinho.services import obter_carrinho
from .models import Pedido, PedidoItem


def pagamento(request):

    carrinho = obter_carrinho(request)

    if not carrinho.itens.exists():
        return redirect("ver_carrinho")

    # calcular totais
    total_produtos = sum(item.subtotal for item in carrinho.itens.all())

    frete = request.session.get("frete")
    valor_frete = Decimal(frete["valor"]) if frete else Decimal("0.00")

    total_geral = total_produtos + valor_frete

    if request.method == "POST":

        pedido = Pedido.objects.create(
            usuario=request.user if request.user.is_authenticated else None,
            total_produtos=total_produtos,
            valor_frete=valor_frete,
            total_geral=total_geral,
            cep_entrega=frete.get("cep", "") if frete else ""
        )

        for item in carrinho.itens.all():
            PedidoItem.objects.create(
                pedido=pedido,
                produto=item.produto,
                preco_unitario=item.preco_unitario,
                quantidade=item.quantidade,
                opcoes=item.opcoes
            )

        # limpar carrinho
        carrinho.itens.all().delete()

        return redirect("pedidos:pedido_confirmado", pedido_id=pedido.id)

    return render(request, "pedidos/pagamento.html", {
        "carrinho": carrinho,
        "total_produtos": total_produtos,
        "frete": frete,
        "total_geral": total_geral,
    })


def pedido_confirmado(request, pedido_id):

    pedido = get_object_or_404(Pedido, id=pedido_id)

    return render(request, "pedidos/pedido_confirmado.html", {
        "pedido": pedido
    })