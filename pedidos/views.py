from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from carrinho.services import obter_carrinho
from carrinho.views import validar_e_limpar_frete
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
from django.views.decorators.http import require_POST
from app.models import UserProfile


logger = logging.getLogger(__name__)


def formatar_cpf_para_exibicao(cpf):
    if not cpf:
        return ''
    cpf_limpo = ''.join(filter(str.isdigit, str(cpf)))
    if len(cpf_limpo) == 11:
        return f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
    return cpf


def _salvar_dados_no_profile(user, endereco, cpf_limpo=None, telefone=None):
    """
    Persiste endereço, CPF e telefone no UserProfile após a compra.
    Regras:
      - Só salva campos válidos (não vazio)
      - Não sobrescreve campos existentes com vazios
    """
    try:
        profile, _ = UserProfile.objects.get_or_create(user=user)

        campos_endereco = [
            "nome_completo", "cep", "rua", "numero",
            "complemento", "bairro", "cidade", "estado",
        ]
        for campo in campos_endereco:
            valor_novo = (endereco.get(campo) or "").strip()
            if valor_novo:
                setattr(profile, campo, valor_novo)

        if cpf_limpo and len(cpf_limpo) == 11:
            profile.cpf = cpf_limpo

        # Salva telefone/WhatsApp se fornecido
        if telefone:
            telefone_limpo = ''.join(filter(str.isdigit, telefone))
            if len(telefone_limpo) >= 10:
                profile.telefone = telefone_limpo

        profile.save()
    except Exception:
        logger.exception(f"Erro ao salvar dados no profile do usuário {user.id}")


@login_required
def pagamento(request):
    carrinho = obter_carrinho(request)

    if not carrinho.itens.exists():
        return redirect("ver_carrinho")

    validar_e_limpar_frete(request, carrinho)

    tipo_entrega = request.session.get("tipo_entrega", "entrega")
    is_retirada = tipo_entrega == "retirada"

    total_produtos = sum(item.subtotal for item in carrinho.itens.all())
    frete = request.session.get("frete")
    valor_frete = Decimal(frete["valor"]) if frete and not is_retirada else Decimal("0.00")
    total_geral = total_produtos + valor_frete

    desconto_pix = total_geral * Decimal("0.05")
    total_com_desconto = total_geral - desconto_pix

    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    cpf_formatado = formatar_cpf_para_exibicao(profile.cpf)

    if request.method == "POST":
        metodo = request.POST.get("metodo")
        frete_sessao = request.session.get("frete") or {}
        endereco = request.session.get("endereco", {})
        whatsapp_retirada = request.session.get("whatsapp_retirada", "")

        # Para entrega, valida endereço. Para retirada, pula.
        if not is_retirada:
            if not endereco or not endereco.get("cep") or not endereco.get("rua"):
                return redirect("carrinho:finalizar_compra")

            from carrinho.services.endereco_service import validar_endereco
            eh_valido, erros = validar_endereco(endereco)
            if not eh_valido:
                return JsonResponse({"status": "erro", "mensagens": erros}, status=400)

        cpf = request.POST.get("cpf") or request.POST.get("cpf-boleto") or ""
        cpf_limpo = ''.join(filter(str.isdigit, cpf))

        if metodo in ["cartao", "boleto"]:
            if not cpf_limpo or len(cpf_limpo) != 11:
                return JsonResponse({"status": "erro", "mensagem": "CPF inválido."}, status=400)
        else:
            cpf_limpo = None

        try:
            pedido = criar_pedido(
                usuario=request.user,
                carrinho=carrinho,
                frete=frete_sessao if not is_retirada else {},
                endereco=endereco,
                cpf=cpf_limpo,
            )
            pedido.status = "aguardando_pagamento"

            # Salva tipo de entrega e WhatsApp no pedido
            pedido.tipo_entrega = tipo_entrega
            pedido.whatsapp_retirada = whatsapp_retirada
            pedido.save()

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
                pagamento_obj = criar_pagamento_pix(pedido, valor=total_com_desconto)
                _salvar_dados_no_profile(request.user, endereco, telefone=whatsapp_retirada)
                request.session.pop("resumo_checkout", None)
                request.session.pop("frete", None)
                return render(request, "pedidos/pagamentos/pix.html", {
                    "pedido": pedido,
                    "pagamento": pagamento_obj,
                    "etapa": 3,
                })

            if metodo == "boleto":
                pagamento_obj = criar_pagamento_boleto(pedido)
                _salvar_dados_no_profile(request.user, endereco, cpf_limpo, telefone=whatsapp_retirada)
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

                    _salvar_dados_no_profile(request.user, endereco, cpf_limpo, telefone=whatsapp_retirada)
                    carrinho.itens.all().delete()
                    request.session.pop("resumo_checkout", None)
                    request.session.pop("frete", None)
                    request.session.pop("tipo_entrega", None)
                    request.session.pop("whatsapp_retirada", None)
                    return redirect("pedidos:pedido_confirmado", pedido_id=pedido.id)

                pedido.status = "aguardando_pagamento"
                pedido.save()
                return redirect("pedidos:pagamento")

        except ValidationError as e:
            return JsonResponse({"status": "erro", "mensagem": str(e)}, status=400)
        except Exception as e:
            logger.exception(f"Erro inesperado ao processar pedido do usuário {request.user.id}")
            return JsonResponse({"status": "erro", "mensagem": f"Erro ao processar pedido: {str(e)}"}, status=500)

    # GET
    return render(request, "pedidos/pagamento.html", {
        "total_produtos":      total_produtos,
        "frete":               frete if not is_retirada else None,
        "total_geral":         total_geral,
        "desconto_pix":        desconto_pix,
        "total_com_desconto":  total_com_desconto,
        "mp_public_key":       settings.MERCADO_PAGO_PUBLIC_KEY,
        "etapa":               3,
        "btn_confirmar":       True,
        "cpf":                 cpf_formatado,
        "is_retirada":         is_retirada,
    })


@login_required
def pedido_confirmado(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    return render(request, "pedidos/pedido_confirmado.html", {"pedido": pedido, "etapa": 4})


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
        .prefetch_related("itens", "itens__produto", "itens__produto__imagens")
    )
    return render(request, "pedidos/meus_pedidos.html", {"pedidos": pedidos})


@login_required
def pedido_detalhe(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    return render(request, "pedidos/pedido_detalhe.html", {"pedido": pedido})


def pedido_enviado(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    return render(request, "pedidos/pedido_enviado.html", {"pedido": pedido})


@require_POST
def salvar_endereco(request):
    data = {
        "nome":        request.POST.get("nome"),
        "cep":         request.POST.get("cep_entrega"),
        "rua":         request.POST.get("rua"),
        "numero":      request.POST.get("numero"),
        "complemento": request.POST.get("complemento"),
        "bairro":      request.POST.get("bairro"),
        "cidade":      request.POST.get("cidade"),
        "estado":      request.POST.get("estado"),
    }
    request.session["endereco"] = data
    return JsonResponse({"status": "ok"})