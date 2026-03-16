from decimal import Decimal
from pedidos.models import Pedido, PedidoItem


def criar_pedido(usuario, carrinho, frete):

    total_produtos = sum(item.subtotal for item in carrinho.itens.all())
    valor_frete = Decimal(frete["valor"]) if frete and frete.get("valor") else Decimal("0")
    total = total_produtos + valor_frete

    pedido = Pedido.objects.create(
        usuario=usuario,
        total=total,
        cep_entrega=frete["cep"] if frete else "",
        rua=frete.get("rua", "") if frete else "",
        bairro=frete.get("bairro", "") if frete else "",
        cidade=frete.get("cidade", "") if frete else "",
        estado=frete.get("estado", "") if frete else "",
    )

    for item in carrinho.itens.all():
        PedidoItem.objects.create(
            pedido=pedido,
            produto=item.produto,
            quantidade=item.quantidade,
            preco_unitario=item.preco_unitario,
            opcoes=item.opcoes or {}
        )

    return pedido