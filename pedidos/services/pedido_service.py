from decimal import Decimal
from django.core.exceptions import ValidationError
from pedidos.models import Pedido, PedidoItem


def criar_pedido(usuario, carrinho, frete, endereco):
    """
    Cria um pedido validando todos os itens do carrinho.
    """
    
    # ✅ VALIDA ITENS DO CARRINHO
    itens = carrinho.itens.select_related("produto")
    
    if not itens.exists():
        raise ValidationError("Carrinho vazio")
    
    # ✅ VERIFICA SE PRODUTO AINDA EXISTE E PRECO ESTÁ CORRETO
    total_produtos = Decimal("0.00")
    
    for item in itens:
        if item.quantidade < 1:
            raise ValidationError(f"Quantidade inválida para {item.produto.nome}")
        
        # ✅ VERIFICA SE PRECO ATUAL BATE COM O QUE FOI ADICIONADO
        if item.preco_unitario != item.produto.preco:
            # Avisa mas não bloqueia (preco pode ter mudado)
            item.preco_unitario = item.produto.preco
            item.save()
        
        total_produtos += item.subtotal
    
    # ✅ VALIDA FRETE
    valor_frete = Decimal(frete["valor"]) if frete and frete.get("valor") else Decimal("0")
    
    if valor_frete < 0:
        raise ValidationError("Frete não pode ser negativo")
    
    if valor_frete > Decimal("500.00"):
        raise ValidationError("Frete muito alto, possível fraude")
    
    total = total_produtos + valor_frete
    
    # ✅ CRIA O PEDIDO
    pedido = Pedido.objects.create(
        usuario=usuario,
        total=total,
        cep_entrega=endereco.get("cep", ""),
        rua=endereco.get("rua", ""),
        numero=endereco.get("numero", ""),
        complemento=endereco.get("complemento", ""),
        bairro=endereco.get("bairro", ""),
        cidade=endereco.get("cidade", ""),
        estado=endereco.get("estado", ""),
    )

    for item in itens:
        PedidoItem.objects.create(
            pedido=pedido,
            produto=item.produto,
            quantidade=item.quantidade,
            preco_unitario=item.preco_unitario,
            opcoes=item.opcoes or {}
        )

    return pedido