from decimal import Decimal
from pedidos.models import Pedido, PedidoItem


def criar_pedido(usuario, carrinho, frete, endereco):

    total_produtos = sum(item.subtotal for item in carrinho.itens.all())
    valor_frete = Decimal(frete["valor"]) if frete and frete.get("valor") else Decimal("0")
    total = total_produtos + valor_frete

    pedido = Pedido.objects.create(
        usuario=usuario,
        total=total,

        cep_entrega=endereco.get("cep_entrega", ""),
        rua=endereco.get("rua", ""),
        numero=endereco.get("numero", ""),
        complemento=endereco.get("complemento", ""),
        bairro=endereco.get("bairro", ""),
        cidade=endereco.get("cidade", ""),
        estado=endereco.get("estado", ""),
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