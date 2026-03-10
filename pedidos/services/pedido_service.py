from pedidos.models import Pedido, PedidoItem


def criar_pedido(usuario, carrinho, frete):

    total = sum(item.subtotal for item in carrinho.itens.all())

    pedido = Pedido.objects.create(
        usuario=usuario,
        total=total,
        cep_entrega=frete["cep"]
    )

    for item in carrinho.itens.all():

        PedidoItem.objects.create(
            pedido=pedido,
            produto=item.produto,
            quantidade=item.quantidade,
            preco_unitario=item.preco_unitario
        )

    return pedido