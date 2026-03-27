from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from carrinho.services import obter_carrinho
from .models import Pedido
from pedidos.services.pedido_service import criar_pedido
from pedidos.services.pagamento_service import (
    criar_pagamento_pix,
    criar_pagamento_boleto,
    criar_pagamento_cartao,
)
from pedidos.services.antifraude_service import validar_pedido_com_motivo
from pedidos.services.parcelamento_service import obter_parcelas
from pedidos.services.email_service import (
    enviar_email_pedido_confirmado,
    enviar_email_pedido_enviado,
)
import logging

logger = logging.getLogger(__name__)


@login_required
def pagamento(request):
    carrinho = obter_carrinho(request)

    if not carrinho.itens.exists():
        return redirect("ver_carrinho")

    total_produtos = sum(item.subtotal for item in carrinho.itens.all())
    frete = request.session.get("frete")
    valor_frete = Decimal(frete["valor"]) if frete else Decimal("0.00")
    total_geral = total_produtos + valor_frete

    # Desconto para PIX (5%)
    desconto_pix = total_geral * Decimal("0.05")
    total_com_desconto = total_geral - desconto_pix

    if request.method == "POST":
        metodo = request.POST.get("metodo")
        frete_sessao = request.session.get("frete") or {}
        endereco = request.session.get("endereco", {})

        # Validação de endereço
        if not endereco or not endereco.get("cep") or not endereco.get("rua"):
            return redirect("carrinho:finalizar_compra")

        from carrinho.services.endereco_service import validar_endereco
        eh_valido, erros = validar_endereco(endereco)
        if not eh_valido:
            return JsonResponse({"status": "erro", "mensagens": erros}, status=400)

        # Validação de CPF — aceita tanto "cpf" (pix/cartão) quanto "cpf-boleto"
        cpf = (
            request.POST.get("cpf")
            or request.POST.get("cpf-boleto")
            or ""
        ).strip()

        if not cpf or len(cpf.replace(".", "").replace("-", "")) != 11:
            return JsonResponse({"status": "erro", "mensagem": "CPF inválido."}, status=400)

        try:
            # Cria o pedido UMA ÚNICA VEZ com todos os dados, incluindo CPF
            pedido = criar_pedido(
                usuario=request.user,
                carrinho=carrinho,
                frete=frete_sessao,
                endereco=endereco,
                cpf=cpf,
            )
            pedido.status = "aguardando_pagamento"
            pedido.save()

            # Validação de antifraude
            valido, motivo = validar_pedido_com_motivo(pedido)
            if not valido:
                pedido.status = "cancelado"
                pedido.save()
                request.session.pop("resumo_checkout", None)
                return JsonResponse({
                    "status": "erro",
                    "mensagem": f"Pedido não passou na validação de antifraude. Motivo: {motivo}"
                }, status=400)

            # Processamento conforme método
            if metodo == "pix":
                pagamento_obj = criar_pagamento_pix(pedido, valor=total_com_desconto)
                request.session.pop("resumo_checkout", None)
                request.session.pop("frete", None)
                return render(request, "pedidos/pagamentos/pix.html", {
                    "pedido": pedido,
                    "pagamento": pagamento_obj,
                    "etapa": 3,
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

                if pagamento_obj.status == "aprovado":
                    if pedido.status != "pago":
                        pedido.status = "pago"
                        pedido.save()
                        enviar_email_pedido_confirmado(pedido)

                    carrinho.itens.all().delete()
                    request.session.pop("resumo_checkout", None)
                    request.session.pop("frete", None)
                    return redirect("pedidos:pedido_confirmado", pedido_id=pedido.id)

                pedido.status = "aguardando_pagamento"
                pedido.save()
                return redirect("pedidos:pagamento")

        except ValidationError as e:
            return JsonResponse({"status": "erro", "mensagem": str(e)}, status=400)
        except Exception as e:
            logger.exception(f"Erro inesperado ao processar pedido do usuário {request.user.id}")
            return JsonResponse({
                "status": "erro",
                "mensagem": f"Erro ao processar pedido: {str(e)}"
            }, status=500)

    # GET – renderiza a página
    return render(request, "pedidos/pagamento.html", {
        "total_produtos": total_produtos,
        "frete": frete,
        "total_geral": total_geral,
        "desconto_pix": desconto_pix,
        "total_com_desconto": total_com_desconto,
        "mp_public_key": settings.MERCADO_PAGO_PUBLIC_KEY,
        "etapa": 3,
        "btn_confirmar": True,
    })


@login_required
def pedido_confirmado(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    return render(request, "pedidos/pedido_confirmado.html", {
        "pedido": pedido,
        "etapa": 4,
    })


@login_required
def verificar_pagamento(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    return JsonResponse({"pago": pedido.status == "pago"})


def parcelas_cartao(request):
    valor = request.GET.get("valor", 0)
    bandeira = request.GET.get("bandeira", "")
    parcelas = obter_parcelas(valor, bandeira)
    return JsonResponse(parcelas, safe=False)


@login_required
def meus_pedidos(request):
    pedidos = (
        Pedido.objects
        .filter(usuario=request.user)
        .order_by("-criado_em")
        .prefetch_related(
            "itens",
            "itens__produto",
            "itens__produto__imagens",
        )
    )
    return render(request, "pedidos/meus_pedidos.html", {"pedidos": pedidos})


@login_required
def pedido_detalhe(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    return render(request, "pedidos/pedido_detalhe.html", {"pedido": pedido})


def pedido_enviado(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    return render(request, "pedidos/pedido_enviado.html", {"pedido": pedido})