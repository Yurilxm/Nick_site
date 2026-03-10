from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from carrinho.services import obter_carrinho
from .models import Pedido
from pedidos.services.pedido_service import criar_pedido
from pedidos.services.pagamento_service import (criar_pagamento_pix, criar_pagamento_boleto, criar_pagamento_cartao)
from pedidos.services.antifraude_service import validar_pedido
from django.http import JsonResponse
from pedidos.services.parcelamento_service import obter_parcelas


@login_required
def pagamento(request):

    carrinho = obter_carrinho(request)

    if not carrinho.itens.exists():
        return redirect("ver_carrinho")

    frete = request.session.get("frete")

    if request.method == "POST":

        metodo = request.POST.get("metodo")

        # cria pedido
        pedido = criar_pedido(request.user, carrinho, frete)

        # antifraude
        if not validar_pedido(pedido):

            pedido.status = "cancelado"
            pedido.save()

            return redirect("loja")

        # ========================
        # PIX
        # ========================

        if metodo == "pix":

            pagamento = criar_pagamento_pix(pedido)

            return render(
                request,
                "pedidos/pagamentos/pix.html",
                {
                    "pedido": pedido,
                    "pagamento": pagamento,
                }
            )

        # ========================
        # BOLETO
        # ========================

        if metodo == "boleto":

            pagamento = criar_pagamento_boleto(pedido)

            return redirect(pagamento.boleto_url)

        # ========================
        # CARTÃO
        # ========================

        if metodo == "cartao":

            token = request.POST.get("token")
            parcelas = request.POST.get("parcelas")

            pagamento = criar_pagamento_cartao(
                pedido,
                token,
                parcelas
            )

            if pagamento.status == "aprovado":

                pedido.status = "pago"
                pedido.save()

                return redirect(
                    "pedidos:pedido_confirmado",
                    pedido_id=pedido.id
                )

            return redirect(
                "pedidos:pagamento",
            )

    return render(
        request,
        "pedidos/pagamento.html"
    )


@login_required
def pedido_confirmado(request, pedido_id):

    pedido = get_object_or_404(
        Pedido,
        id=pedido_id,
        usuario=request.user
    )

    return render(
        request,
        "pedidos/pedido_confirmado.html",
        {
            "pedido": pedido
        }
    )


def parcelas_cartao(request):

    valor = request.GET.get("valor")
    bandeira = request.GET.get("bandeira")

    parcelas = obter_parcelas(valor, bandeira)

    return JsonResponse(parcelas, safe=False)