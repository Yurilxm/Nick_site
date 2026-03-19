from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse
from carrinho.services import obter_carrinho
from .models import Pedido
from pedidos.services.pedido_service import criar_pedido
from pedidos.services.pagamento_service import (criar_pagamento_pix, criar_pagamento_boleto, criar_pagamento_cartao,)
from pedidos.services.antifraude_service import validar_pedido
from pedidos.services.parcelamento_service import obter_parcelas
from pedidos.services.email_service import enviar_email_pedido_confirmado


@login_required
def pagamento(request):
    carrinho = obter_carrinho(request)

    if not carrinho.itens.exists():
        return redirect("ver_carrinho")

    resumo = request.session.get("resumo_checkout", {})
    frete = resumo.get("frete") or request.session.get("frete")
    total_produtos = Decimal(resumo.get("total_produtos", "0"))
    valor_frete = Decimal(resumo.get("valor_frete", "0"))
    total_geral = Decimal(resumo.get("total_geral", "0"))

    if request.method == "POST":
        metodo = request.POST.get("metodo")
        frete_sessao = request.session.get("frete") or {}
        endereco = request.session.get("endereco", {})

        if not endereco or not endereco.get("cep") or not endereco.get("rua"):
            return redirect("carrinho:checkout")

        pedido = criar_pedido(request.user, carrinho, frete_sessao, endereco)
        pedido.status = "aguardando_pagamento"
        pedido.save()

        if not validar_pedido(pedido):
            pedido.status = "cancelado"
            pedido.save()
            # Limpa sessão mas NÃO limpa carrinho — pedido foi cancelado
            request.session.pop("resumo_checkout", None)
            return redirect("home")

        if metodo == "pix":
            pagamento_obj = criar_pagamento_pix(pedido)
            request.session.pop("resumo_checkout", None)
            request.session.pop("frete", None)
            return render(request, "pedidos/pagamentos/pix.html", {
                "pedido": pedido,
                "pagamento": pagamento_obj,
            })

        if metodo == "boleto":
            pagamento_obj = criar_pagamento_boleto(pedido)
            request.session.pop("resumo_checkout", None)
            request.session.pop("frete", None)
            return redirect(pagamento_obj.boleto_url)

        if metodo == "cartao":
            token = request.POST.get("card_token")
            parcelas = request.POST.get("parcelas", "1")
            bandeira = request.POST.get("card_bandeira", "visa")

            pagamento_obj = criar_pagamento_cartao(pedido, token, parcelas, bandeira)

            if pagamento_obj.status in ("aprovado", "approved"):

                if pedido.status != "pago":
                    pedido.status = "pago"
                    pedido.save()

                    enviar_email_pedido_confirmado(pedido)

                carrinho.itens.all().delete()
                request.session.pop("resumo_checkout", None)
                request.session.pop("frete", None)
                return redirect("pedidos:pedido_confirmado", pedido_id=pedido.id)

            # Cartão recusado — mantém carrinho e sessão intactos
            pedido.status = "aguardando_pagamento"
            pedido.save()
            return redirect("pedidos:pagamento")

    return render(request, "pedidos/pagamento.html", {
        "total_produtos": total_produtos,
        "frete": frete,
        "total_geral": total_geral,
        "mp_public_key": settings.MERCADO_PAGO_PUBLIC_KEY,
    })


@login_required
def pedido_confirmado(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    return render(request, "pedidos/pedido_confirmado.html", {"pedido": pedido})


@login_required
def verificar_pagamento(request, pedido_id):
    """Polling do pix.js — verifica se o pedido foi pago."""
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    return JsonResponse({"pago": pedido.status == "pago"})


def parcelas_cartao(request):
    valor = request.GET.get("valor", 0)
    bandeira = request.GET.get("bandeira", "")
    parcelas = obter_parcelas(valor, bandeira)
    return JsonResponse(parcelas, safe=False)


@login_required
def meus_pedidos(request):
    pedidos = Pedido.objects.filter(
        usuario=request.user
    ).order_by("-criado_em")
    return render(request, "pedidos/meus_pedidos.html", {"pedidos": pedidos})