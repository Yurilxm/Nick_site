from decimal import Decimal
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.conf import settings
from app.models import UserProfile
from produtos.models import Produto, GrupoOpcao, Opcao
from .models import ItemCarrinho
from .services import obter_carrinho
from carrinho.services.melhor_envio_service import calcular_frete_melhor_envio
from carrinho.services.endereco_service import validar_endereco


# ============================================================
# HELPERS
# ============================================================

def calcular_total_produtos(carrinho):
    return sum(
        (item.subtotal for item in carrinho.itens.all()),
        Decimal("0.00")
    )


def traduzir_opcoes(itens):
    for item in itens:
        opcoes_traduzidas = []
        for chave, valor in item.opcoes.items():
            if chave == "personalizacao":
                opcoes_traduzidas.append({"grupo": "Personalização", "valores": [valor]})
                continue
            try:
                grupo = GrupoOpcao.objects.get(id=int(chave))
                if isinstance(valor, list):
                    opcoes = Opcao.objects.filter(id__in=valor)
                    nomes = [op.nome for op in opcoes]
                else:
                    nomes = [valor]
                opcoes_traduzidas.append({"grupo": grupo.nome, "valores": nomes})
            except (GrupoOpcao.DoesNotExist, ValueError):
                continue
        item.opcoes_formatadas = opcoes_traduzidas


def validar_e_limpar_frete(request, carrinho):
    """
    Função CENTRAL de validação do frete na sessão.
    Limpa session["frete"] se qualquer condição inválida detectada:
      - tipo_entrega == "retirada"
      - carrinho vazio
      - frete sem CEP
      - CEP do frete diverge do endereço salvo
    """
    # Retirada nunca tem frete
    if request.session.get("tipo_entrega") == "retirada":
        request.session.pop("frete", None)
        return

    frete = request.session.get("frete")

    if not carrinho.itens.exists():
        request.session.pop("frete", None)
        return

    if not frete:
        return

    cep_frete = frete.get("cep", "").replace("-", "").strip()
    if not cep_frete or len(cep_frete) != 8:
        request.session.pop("frete", None)
        return

    endereco_sessao = request.session.get("endereco", {})
    cep_endereco = endereco_sessao.get("cep", "").replace("-", "").strip() if endereco_sessao else ""
    if cep_endereco and cep_endereco != cep_frete:
        request.session.pop("frete", None)


# ============================================================
# VIEWS
# ============================================================

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
            if len(valores) == 1:
                valor = valores[0].strip()
                if valor.isdigit():
                    opcoes_escolhidas[grupo_id] = [valor]
                elif valor:
                    opcoes_escolhidas[grupo_id] = valor
            elif valores:
                opcoes_escolhidas[grupo_id] = valores

    if personalizacao:
        opcoes_escolhidas["personalizacao"] = personalizacao

    item = ItemCarrinho.objects.filter(
        carrinho=carrinho, produto=produto, opcoes=opcoes_escolhidas
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
    validar_e_limpar_frete(request, carrinho)
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
    validar_e_limpar_frete(request, carrinho)
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
def limpar_frete(request):
    request.session.pop("frete", None)
    return JsonResponse({"status": "ok"})


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

    validar_e_limpar_frete(request, carrinho)

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
    traduzir_opcoes(itens)

    lista_itens = []
    for item in itens:
        opcao_principal = None
        if hasattr(item, "opcoes_formatadas") and item.opcoes_formatadas:
            opc = item.opcoes_formatadas[0]
            opcao_principal = f"{opc['grupo']}: {', '.join(opc['valores'])}"
        lista_itens.append({
            "id": item.id,
            "nome": item.produto.nome,
            "quantidade": item.quantidade,
            "preco": float(item.preco_unitario),
            "imagem": item.produto.imagem.url if item.produto.imagem else "",
            "url": item.produto.get_absolute_url(),
            "opcao": opcao_principal
        })

    return JsonResponse({
        "quantidade_total": sum(item.quantidade for item in itens),
        "total": float(calcular_total_produtos(carrinho)),
        "itens": lista_itens
    })


@require_POST
def calcular_frete(request):
    cep = request.POST.get("cep", "").replace("-", "").strip()
    carrinho = obter_carrinho(request)
    itens = carrinho.itens.select_related("produto")

    if not cep or len(cep) != 8:
        return JsonResponse({"status": "erro", "mensagem": "CEP inválido."})
    if not itens.exists():
        return JsonResponse({"status": "erro", "mensagem": "Carrinho vazio."})

    opcoes = calcular_frete_melhor_envio(cep, itens)
    if not opcoes:
        return JsonResponse({"status": "erro", "mensagem": "Não foi possível calcular o frete para este CEP."})

    melhor = opcoes[0]
    request.session["frete"] = {
        "cep": cep,
        "valor": str(melhor["preco"]),
        "tipo": melhor["nome"],
        "prazo": melhor["prazo"],
        "transportadora": melhor["transportadora"],
    }
    return JsonResponse({"status": "ok", "opcoes": opcoes, "frete": request.session["frete"]})


@require_POST
def selecionar_frete(request):
    import json
    data = json.loads(request.body)
    request.session["frete"] = {
        "cep": data.get("cep"),
        "valor": str(data.get("valor")),
        "tipo": data.get("nome"),
        "prazo": data.get("prazo"),
        "transportadora": data.get("transportadora"),
    }
    return JsonResponse({"status": "ok"})


@login_required
def finalizar_compra(request):
    carrinho = obter_carrinho(request)

    if not carrinho.itens.exists():
        return redirect("ver_carrinho")

    itens = carrinho.itens.select_related("produto")
    traduzir_opcoes(itens)
    validar_e_limpar_frete(request, carrinho)
    total_produtos = calcular_total_produtos(carrinho)

    if request.method == "POST":
        tipo_entrega = request.POST.get("tipo_entrega", "entrega")
        request.session["tipo_entrega"] = tipo_entrega

        if tipo_entrega == "retirada":
            # ✅ Retirada: sem endereço, sem frete
            nome = request.POST.get("nome_completo") or request.POST.get("nome_completo_retirada", "")
            whatsapp = ''.join(filter(str.isdigit, request.POST.get("whatsapp_retirada", "")))
            request.session.pop("frete", None)
            request.session["endereco"] = {
                "nome_completo": nome,
                "cep": "", "rua": "", "numero": "",
                "complemento": "", "bairro": "", "cidade": "", "estado": "",
            }
            request.session["whatsapp_retirada"] = whatsapp
        else:
            # ✅ Entrega normal
            request.session["whatsapp_retirada"] = ""
            request.session["endereco"] = {
                "nome_completo": request.POST.get("nome_completo", ""),
                "cep":           request.POST.get("cep_entrega", ""),
                "rua":           request.POST.get("rua", ""),
                "numero":        request.POST.get("numero", ""),
                "complemento":   request.POST.get("complemento", ""),
                "bairro":        request.POST.get("bairro", ""),
                "cidade":        request.POST.get("cidade", ""),
                "estado":        request.POST.get("estado", ""),
            }
            validar_e_limpar_frete(request, carrinho)

        return redirect("pedidos:pagamento")

    # GET
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    endereco_sessao = request.session.get("endereco")
    endereco_profile = {
        "nome_completo": profile.nome_completo,
        "cep":           profile.cep,
        "rua":           profile.rua,
        "numero":        profile.numero,
        "complemento":   profile.complemento,
        "bairro":        profile.bairro,
        "cidade":        profile.cidade,
        "estado":        profile.estado,
    }

    if not any(endereco_profile.values()):
        request.session.pop("endereco", None)
        endereco = {}
    else:
        endereco = {**endereco_profile, **endereco_sessao} if endereco_sessao else endereco_profile

    if not isinstance(endereco, dict):
        endereco = {}

    tipo_entrega_sessao = request.session.get("tipo_entrega", "entrega")

    if tipo_entrega_sessao == "entrega":
        if not endereco.get("cep"):
            request.session.pop("frete", None)
        elif not request.session.get("frete"):
            opcoes = calcular_frete_melhor_envio(endereco["cep"], itens)
            if opcoes:
                melhor = opcoes[0]
                request.session["frete"] = {
                    "cep":            endereco["cep"],
                    "valor":          str(melhor["preco"]),
                    "tipo":           melhor["nome"],
                    "prazo":          melhor["prazo"],
                    "transportadora": melhor["transportadora"],
                }

    frete = request.session.get("frete")
    valor_frete = Decimal(frete["valor"]) if frete else Decimal("0.00")
    total_geral = total_produtos + valor_frete

    whatsapp_salvo = request.session.get("whatsapp_retirada") or profile.telefone or ""

    return render(request, "carrinho/checkout.html", {
        "itens":               itens,
        "total_produtos":      total_produtos,
        "frete":               frete,
        "total_geral":         total_geral,
        "endereco":            endereco,
        "etapa":               2,
        "tipo_entrega_sessao": tipo_entrega_sessao,
        "whatsapp_salvo":      whatsapp_salvo,
        "loja_endereco":       settings.LOJA_ENDERECO,
    })