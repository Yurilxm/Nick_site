from django.shortcuts import get_object_or_404, redirect, render
from produtos.models import Produto
from .models import ItemCarrinho
from .services import obter_carrinho
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db.models import Sum


@require_POST
def adicionar_ao_carrinho(request, produto_id):
    carrinho = obter_carrinho(request)
    produto = get_object_or_404(Produto, id=produto_id)

    item, created = ItemCarrinho.objects.get_or_create(
        carrinho=carrinho, produto=produto, defaults={'preco_unitario': produto.preco}
    )

    if not created:
        item.quantidade += 1
        item.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok'})

    return redirect('ver_carrinho')

@require_POST
def remover_do_carrinho(request, item_id):
    carrinho = obter_carrinho(request)

    item = get_object_or_404(ItemCarrinho, id=item_id, carrinho=carrinho)

    item.delete()
    
     # 👉 Se for AJAX, responde JSON
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        itens = carrinho.itens.select_related("produto")

        return JsonResponse({
            "quantidade_total": sum(i.quantidade for i in itens),
            "total": float(sum(i.subtotal for i in itens)),
            "itens": [
                {
                    "id": i.id,
                    "nome": i.produto.nome,
                    "quantidade": i.quantidade,
                    "subtotal": float(i.subtotal),
                }
                for i in itens
            ],
            "removido_id": item_id,
        })

    # 👉 fallback (caso alguém acesse sem JS)
    return redirect('ver_carrinho')


def ver_carrinho(request):
    carrinho = obter_carrinho(request)
    itens = carrinho.itens.select_related("produto")

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
    item = get_object_or_404(ItemCarrinho, id=item_id, carrinho=carrinho)

    item.quantidade += 1
    item.save()

    # 👉 Se for AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        itens = carrinho.itens.select_related("produto")

        return JsonResponse({
            "quantidade_item": item.quantidade,
            "subtotal_item": float(item.subtotal),
            "quantidade_total": sum(i.quantidade for i in itens),
            "total": float(sum(i.subtotal for i in itens)),
            "itens": [
                {
                    "id": i.id,
                    "nome": i.produto.nome,
                    "quantidade": i.quantidade,
                    "subtotal": float(i.subtotal),
                }
                for i in itens
            ],
        })

    # 👉 Fallback (caso alguém acesse sem JS)
    return redirect('ver_carrinho')


@require_POST
def diminuir_quantidade(request, item_id):
    carrinho = obter_carrinho(request)
    item = get_object_or_404(ItemCarrinho, id=item_id, carrinho=carrinho)

    if item.quantidade > 1:
        item.quantidade -= 1
        item.save()
        removido = False
    else:
        item.delete()
        removido = True

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        itens = carrinho.itens.select_related("produto")

        return JsonResponse({
            "removido": removido,
            "item_id": item_id,
            "quantidade_item": item.quantidade if not removido else 0,
            "subtotal_item": float(item.subtotal) if not removido else 0,
            "quantidade_total": sum(i.quantidade for i in itens),
            "total": float(sum(i.subtotal for i in itens)),
            "itens": [
                {
                    "id": i.id,
                    "nome": i.produto.nome,
                    "quantidade": i.quantidade,
                    "subtotal": float(i.subtotal),
                }
                for i in itens
            ],
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
                "imagem": item.produto.imagem.url if item.produto.imagem else "",
                "url": item.produto.get_absolute_url(),
            }
            for item in itens
        ]
    })