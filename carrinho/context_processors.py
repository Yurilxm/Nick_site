from .services import obter_carrinho

def carrinho_context(request):
    carrinho = obter_carrinho(request)
    itens = carrinho.itens.all()

    total = sum(item.subtotal for item in itens)
    quantidade = sum(item.quantidade for item in itens)

    return {
        'mini_carrinho_itens': itens,
        'mini_carrinho_total': total,
        'mini_carrinho_quantidade': quantidade,
    }
