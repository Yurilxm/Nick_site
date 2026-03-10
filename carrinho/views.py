from decimal import Decimal
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from produtos.models import Produto, GrupoOpcao, Opcao
from .models import ItemCarrinho
from .services import obter_carrinho


# ==========================
# HELPERS
# ==========================

def limpar_frete_se_carrinho_vazio(request, carrinho):
    if not carrinho.itens.exists():
        request.session.pop("frete", None)


def calcular_total_produtos(carrinho):
    return sum(
        (item.subtotal for item in carrinho.itens.all()),
        Decimal("0.00")
    )


def traduzir_opcoes(itens):
    """Adiciona opcoes_formatadas em cada item do carrinho."""
    for item in itens:
        opcoes_traduzidas = []
        for chave, valor in item.opcoes.items():
            if chave == "personalizacao":
                opcoes_traduzidas.append({
                    "grupo": "Personalização",
                    "valores": [valor]
                })
                continue
            try:
                grupo = GrupoOpcao.objects.get(id=int(chave))
                opcoes = Opcao.objects.filter(id__in=valor)
                opcoes_traduzidas.append({
                    "grupo": grupo.nome,
                    "valores": [op.nome for op in opcoes]
                })
            except (GrupoOpcao.DoesNotExist, ValueError):
                continue
        item.opcoes_formatadas = opcoes_traduzidas


# ==========================
# CARRINHO
# ==========================

@require_POST
def adicionar_ao_carrinho(request, produto_id):
    carrinho = obter_carrinho(request)
    produto = get_object_or_404(Produto, id=produto_id)

    try:
        quantidade = int(request.POST.get("quantidade", 1))
        if quantidade < 1:
            quantidade = 1
    except (ValueError, TypeError):
        quantidade = 1

    personalizacao = request.POST.get("personalizacao", "").strip()

    opcoes_escolhidas = {}
    for key in request.POST:
        if key.startswith("grupo_"):
            grupo_id = key.replace("grupo_", "")
            valores = request.POST.getlist(key)
            if valores:
                opcoes_escolhidas[grupo_id] = valores

    if personalizacao:
        opcoes_escolhidas["personalizacao"] = personalizacao

    item = ItemCarrinho.objects.filter(
        carrinho=carrinho,
        produto=produto,
        opcoes=opcoes_escolhidas
    ).first()

    if item:
        item.quantidade += quantidade
        item.save()
    else:
        ItemCarrinho.objects.create(
            carrinho=carrinho,
            produto=produto,
            preco_unitario=produto.preco,
            quantidade=quantidade,
            opcoes=opcoes_escolhidas
        )

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"status": "ok"})

    return redirect("ver_carrinho")


@require_POST
def remover_do_carrinho(request, item_id):
    carrinho = obter_carrinho(request)
    item = get_object_or_404(ItemCarrinho, id=item_id, carrinho=carrinho)

    item.delete()
    limpar_frete_se_carrinho_vazio(request, carrinho)

    total = calcular_total_produtos(carrinho)

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "quantidade_total": sum(i.quantidade for i in carrinho.itens.all()),
            "total": float(total),
            "carrinho_vazio": not carrinho.itens.exists(),
        })

    return redirect("ver_carrinho")


def ver_carrinho(request):
    carrinho = obter_carrinho(request)
    itens = carrinho.itens.select_related("produto")

    if not itens.exists():
        request.session.pop("frete", None)

    traduzir_opcoes(itens)

    total_produtos = calcular_total_produtos(carrinho)
    frete = request.session.get("frete")
    valor_frete = Decimal(frete["valor"]) if frete else Decimal("0.00")
    total_geral = total_produtos + valor_frete

    return render(request, "carrinho/carrinho.html", {
        "carrinho": carrinho,
        "itens": itens,
        "total_produtos": total_produtos,
        "frete": frete,
        "total_geral": total_geral,
    })


@require_POST
def aumentar_quantidade(request, item_id):
    carrinho = obter_carrinho(request)
    item = get_object_or_404(ItemCarrinho, id=item_id, carrinho=carrinho)

    item.quantidade += 1
    item.save()

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        total = calcular_total_produtos(carrinho)
        return JsonResponse({
            "quantidade_item": item.quantidade,
            "subtotal_item": float(item.subtotal),
            "quantidade_total": sum(i.quantidade for i in carrinho.itens.all()),
            "total": float(total),
        })

    return redirect("ver_carrinho")


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

    limpar_frete_se_carrinho_vazio(request, carrinho)

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        total = calcular_total_produtos(carrinho)
        return JsonResponse({
            "removido": removido,
            "item_id": item_id,
            "quantidade_item": item.quantidade if not removido else 0,
            "subtotal_item": float(item.subtotal) if not removido else 0,
            "quantidade_total": sum(i.quantidade for i in carrinho.itens.all()),
            "total": float(total),
        })

    return redirect("ver_carrinho")


def mini_carrinho_json(request):
    carrinho = obter_carrinho(request)
    itens = carrinho.itens.select_related("produto")

    return JsonResponse({
        "quantidade_total": sum(item.quantidade for item in itens),
        "total": float(calcular_total_produtos(carrinho)),
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


# ==========================
# FRETE
# ==========================

@require_POST
def calcular_frete(request):
    cep = request.POST.get("cep")
    frete_valor = Decimal("29.90")
    frete_tipo = "PAC"

    request.session["frete"] = {
        "cep": cep,
        "valor": str(frete_valor),
        "tipo": frete_tipo,
    }

    return JsonResponse({
        "status": "ok",
        "frete": {
            "cep": cep,
            "valor": str(frete_valor),
            "tipo": frete_tipo,
        }
    })


# ==========================
# FINALIZAR (CHECKOUT)
# ==========================

@login_required
def finalizar_compra(request):
    carrinho = obter_carrinho(request)

    if not carrinho.itens.exists():
        return redirect("ver_carrinho")

    itens = carrinho.itens.select_related("produto")
    traduzir_opcoes(itens)

    total_produtos = calcular_total_produtos(carrinho)
    frete = request.session.get("frete")
    valor_frete = Decimal(frete["valor"]) if frete else Decimal("0.00")
    total_geral = total_produtos + valor_frete

    if request.method == "POST":
        # Salva resumo na sessão para a view de pagamento exibir
        request.session["resumo_checkout"] = {
            "total_produtos": str(total_produtos),
            "valor_frete": str(valor_frete),
            "total_geral": str(total_geral),
            "frete": frete,
        }
        return redirect("pedidos:pagamento")

    return render(request, "carrinho/checkout.html", {
        "itens": itens,
        "total_produtos": total_produtos,
        "frete": frete,
        "total_geral": total_geral,
    })