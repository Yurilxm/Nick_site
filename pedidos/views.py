from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from carrinho.services import obter_carrinho
from .models import Pedido
from pedidos.services.pedido_service import criar_pedido
from pedidos.services.pagamento_service import (criar_pagamento_pix, criar_pagamento_boleto, criar_pagamento_cartao,)
from pedidos.services.antifraude_service import validar_pedido, validar_pedido_com_motivo
from pedidos.services.parcelamento_service import obter_parcelas
from django.db.models import Prefetch
from pedidos.services.email_service import (enviar_email_pedido_confirmado, enviar_email_pedido_enviado,)


@login_required
def pagamento(request):
    carrinho = obter_carrinho(request)

    if not carrinho.itens.exists():
        return redirect("ver_carrinho")

    total_produtos = sum(item.subtotal for item in carrinho.itens.all())
    
    frete = request.session.get("frete")
    valor_frete = Decimal(frete["valor"]) if frete else Decimal("0.00")
    
    if valor_frete > Decimal("500.00"):
        request.session.pop("frete", None)
        return JsonResponse({"status": "erro", "mensagem": "Valor de frete inválido"}, status=400)
    
    total_geral = total_produtos + valor_frete

    if request.method == "POST":
        metodo = request.POST.get("metodo")
        frete_sessao = request.session.get("frete") or {}
        endereco = request.session.get("endereco", {})

        if not endereco or not endereco.get("cep") or not endereco.get("rua"):
            return redirect("carrinho:finalizar_compra")
        
        from carrinho.services.endereco_service import validar_endereco
        eh_valido, erros = validar_endereco(endereco)
        if not eh_valido:
            return JsonResponse({"status": "erro", "mensagens": erros}, status=400)

        try:
            pedido = criar_pedido(request.user, carrinho, frete_sessao, endereco)
            pedido.status = "aguardando_pagamento"
            pedido.save()

            # 🔍 Validação de antifraude com motivo detalhado
            valido, motivo = validar_pedido_com_motivo(pedido)
            
            if not valido:
                pedido.status = "cancelado"
                pedido.save()
                request.session.pop("resumo_checkout", None)
                return JsonResponse({
                    "status": "erro", 
                    "mensagem": f"Pedido não passou na validação de antifraude. Motivo: {motivo}"
                }, status=400)

            if metodo == "pix":
                pagamento_obj = criar_pagamento_pix(pedido)
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

                if pagamento_obj.status in ("aprovado", "approved"):
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
            import traceback
            traceback.print_exc()
            return JsonResponse({"status": "erro", "mensagem": "Erro ao processar pedido. Tente novamente."}, status=500)

    return render(request, "pedidos/pagamento.html", {
        "total_produtos": total_produtos,
        "frete": frete,
        "total_geral": total_geral,
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
            "itens__produto__imagens"
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