from django.shortcuts import get_object_or_404, redirect, render
from produtos.models import Produto
from .models import ItemCarrinho
from .services import obter_carrinho
from django.views.decorators.http import require_POST
from django.http import JsonResponse


@require_POST
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

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok'})

    return redirect('ver_carrinho')


def remover_do_carrinho(request, item_id):
    carrinho = obter_carrinho(request)

    item = get_object_or_404(
        ItemCarrinho,
        id=item_id,
        carrinho=carrinho
    )

    item.delete()
    
     # 👉 Se for AJAX, responde JSON
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        itens = carrinho.itens.all()
        total = sum(i.subtotal for i in itens)

        return JsonResponse({
            'removido': True,
            'total': float(total),
        })

    # 👉 fallback (caso alguém acesse sem JS)
    return redirect('ver_carrinho')


def ver_carrinho(request):
    carrinho = obter_carrinho(request)
    itens = carrinho.itens.all()

    total = sum(item.subtotal for item in itens)

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

    # 👉 Se for AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        itens = carrinho.itens.all()
        total = sum(item.subtotal for item in itens)

        return JsonResponse({
            'quantidade': item.quantidade,
            'subtotal': float(item.subtotal),
            'total': float(total),
        })

    # 👉 Fallback (caso alguém acesse sem JS)
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
        removido = False
    else:
        item.delete()
        removido = True

    # 👉 AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        itens = carrinho.itens.all()
        total = sum(item.subtotal for item in itens)

        return JsonResponse({
            'removido': removido,
            'quantidade': item.quantidade if not removido else 0,
            'subtotal': float(item.subtotal) if not removido else 0,
            'total': float(total),
        })

    return redirect('ver_carrinho')



def mini_carrinho_json(request):
    carrinho = obter_carrinho(request)
    itens = carrinho.itens.select_related("produto")

    return JsonResponse({
        "quantidade_total": sum(item.quantidade for item in itens),
        "total": float(sum(item.subtotal for item in itens)),
        "itens": [
            {
                "id": item.id,
                "nome": item.produto.nome,
                "quantidade": item.quantidade,
                "preco": float(item.preco_unitario),
                "imagem": item.produto.imagem.url if item.produto.imagem else ""
            }
            for item in itens
        ]
    })