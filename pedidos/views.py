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
    
    if valor_frete > Decimal("500.00"):
        request.session.pop("frete", None)
        return JsonResponse({"status": "erro", "mensagem": "Valor de frete inválido"}, status=400)
    
    total_geral = total_produtos + valor_frete

    if request.method == "POST":
        metodo = request.POST.get("metodo")
        frete_sessao = request.session.get("frete") or {}
        endereco = request.session.get("endereco", {})

        print(f"🔵 MÉTODO DE PAGAMENTO: {metodo}")
        print(f"🔵 TOTAL DO PEDIDO: {total_geral}")
        print(f"🔵 ENDEREÇO: {endereco}")

        if not endereco or not endereco.get("cep") or not endereco.get("rua"):
            print("❌ Endereço incompleto, redirecionando para finalizar compra")
            return redirect("carrinho:finalizar_compra")
        
        from carrinho.services.endereco_service import validar_endereco
        eh_valido, erros = validar_endereco(endereco)
        if not eh_valido:
            print(f"❌ Endereço inválido: {erros}")
            return JsonResponse({"status": "erro", "mensagens": erros}, status=400)

        try:
            print("🔵 Criando pedido...")
            pedido = criar_pedido(request.user, carrinho, frete_sessao, endereco)
            pedido.status = "aguardando_pagamento"
            pedido.save()
            print(f"✅ Pedido criado: ID {pedido.id}, Total: R$ {pedido.total}")

            # 🔍 Validação de antifraude com motivo detalhado
            print("🔵 Validando antifraude...")
            valido, motivo = validar_pedido_com_motivo(pedido)
            
            if not valido:
                print(f"❌ Pedido bloqueado pelo antifraude: {motivo}")
                pedido.status = "cancelado"
                pedido.save()
                request.session.pop("resumo_checkout", None)
                return JsonResponse({
                    "status": "erro", 
                    "mensagem": f"Pedido não passou na validação de antifraude. Motivo: {motivo}"
                }, status=400)
            
            print("✅ Antifraude aprovado")

            if metodo == "pix":
                print("🔵 Processando pagamento PIX...")
                pagamento_obj = criar_pagamento_pix(pedido)
                request.session.pop("resumo_checkout", None)
                request.session.pop("frete", None)
                return render(request, "pedidos/pagamentos/pix.html", {
                    "pedido": pedido,
                    "pagamento": pagamento_obj,
                    "etapa": 3,
                })

            if metodo == "boleto":
                print("🔵 Processando pagamento BOLETO...")
                pagamento_obj = criar_pagamento_boleto(pedido)
                print(f"✅ Boleto gerado: {pagamento_obj.boleto_url}")
                request.session.pop("resumo_checkout", None)
                request.session.pop("frete", None)
                return redirect(pagamento_obj.boleto_url)

            if metodo == "cartao":
                token = request.POST.get("card_token")
                parcelas = request.POST.get("parcelas", "1")
                bandeira = request.POST.get("card_bandeira", "visa")
                
                print(f"🔵 Processando pagamento CARTÃO")
                print(f"   Token: {token}")
                print(f"   Parcelas: {parcelas}")
                print(f"   Bandeira: {bandeira}")
                print(f"   Valor total: R$ {pedido.total}")
                
                pagamento_obj = criar_pagamento_cartao(pedido, token, parcelas, bandeira)
                
                print(f"🔵 Status do pagamento: {pagamento_obj.status}")
                print(f"🔵 ID da transação: {pagamento_obj.transaction_id}")
                
                if pagamento_obj.status in ("aprovado", "approved"):
                    print("✅ PAGAMENTO APROVADO!")
                    if pedido.status != "pago":
                        pedido.status = "pago"
                        pedido.save()
                        enviar_email_pedido_confirmado(pedido)
                        print("✅ Email de confirmação enviado")

                    carrinho.itens.all().delete()
                    request.session.pop("resumo_checkout", None)
                    request.session.pop("frete", None)
                    print("🔵 Redirecionando para pedido confirmado")
                    return redirect("pedidos:pedido_confirmado", pedido_id=pedido.id)
                else:
                    print(f"❌ PAGAMENTO RECUSADO! Status: {pagamento_obj.status}")
                    pedido.status = "aguardando_pagamento"
                    pedido.save()
                    print("🔵 Redirecionando de volta para página de pagamento")
                    return redirect("pedidos:pagamento")

        except ValidationError as e:
            print(f"❌ ValidationError: {str(e)}")
            return JsonResponse({"status": "erro", "mensagem": str(e)}, status=400)
        
        except Exception as e:
            import traceback
            print("❌ ERRO INESPERADO:")
            traceback.print_exc()
            return JsonResponse({
                "status": "erro", 
                "mensagem": f"Erro ao processar pedido: {str(e)}"
            }, status=500)

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