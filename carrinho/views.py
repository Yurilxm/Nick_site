from django.shortcuts import get_object_or_404, redirect, render
from produtos.models import Produto
from .models import ItemCarrinho
from .services import obter_carrinho
from django.views.decorators.http import require_POST


def adicionar_ao_carrinho(request, produto_id):
    carrinho = obter_carrinho(request)
    produto = get_object_or_404(Produto, id=produto_id)

    item, created = ItemCarrinho.objects.get_or_create(
        carrinho=carrinho,
        produto=produto,
        defaults={'preco_unitario': produto.preco}
    )

    if not created:
        item.quantidade += 1
        item.save()

    return redirect('ver_carrinho')


def remover_do_carrinho(request, item_id):
    carrinho = obter_carrinho(request)

    item = get_object_or_404(
        ItemCarrinho,
        id=item_id,
        carrinho=carrinho
    )

    item.delete()
    return redirect('ver_carrinho')


def ver_carrinho(request):
    carrinho = obter_carrinho(request)
    itens = carrinho.itens.all()

    total = sum(item.subtotal() for item in itens)

    context = {
        'carrinho': carrinho,
        'itens': itens,
        'total': total,
    }

    return render(request, 'carrinho/carrinho.html', context)


@require_POST
def aumentar_quantidade(request, item_id):
    carrinho = obter_carrinho(request)
    item = get_object_or_404(
        ItemCarrinho,
        id=item_id,
        carrinho=carrinho
    )

    item.quantidade += 1
    item.save()

    return redirect('ver_carrinho')


@require_POST
def diminuir_quantidade(request, item_id):
    carrinho = obter_carrinho(request)
    item = get_object_or_404(
        ItemCarrinho,
        id=item_id,
        carrinho=carrinho
    )

    if item.quantidade > 1:
        item.quantidade -= 1
        item.save()
    else:
        item.delete()

    return redirect('ver_carrinho')