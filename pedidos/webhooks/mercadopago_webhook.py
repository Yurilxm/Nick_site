import json
import hmac
import hashlib
import mercadopago
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from carrinho.models import Carrinho
from pedidos.models import Pagamento

sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)


def _validar_assinatura(request):
    """
    Valida a assinatura HMAC-SHA256 do webhook do MercadoPago.

    O uso de @csrf_exempt neste endpoint é intencional e seguro:
    webhooks são chamadas server-to-server — o servidor do MercadoPago
    não possui nem envia token CSRF. A proteção equivalente é feita aqui
    via validação de assinatura HMAC, conforme documentação oficial:
    https://www.mercadopago.com.br/developers/pt/docs/your-integrations/notifications/webhooks

    Qualquer requisição com assinatura inválida ou ausente retorna HTTP 400.
    """
    secret = getattr(settings, "MERCADO_PAGO_WEBHOOK_SECRET", None)
    if not secret:
        return False

    x_signature = request.headers.get("x-signature", "")
    x_request_id = request.headers.get("x-request-id", "")
    data_id = request.GET.get("data.id", "")

    # Monta o manifest conforme documentação do MercadoPago
    manifest = f"id:{data_id};request-id:{x_request_id};"

    expected = hmac.new(
        secret.encode("utf-8"),
        manifest.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    # Extrai o hash v1 do header x-signature: "ts=....,v1=...."
    hash_recebido = ""
    for parte in x_signature.split(","):
        parte = parte.strip()
        if parte.startswith("v1="):
            hash_recebido = parte[3:]
            break

    return hmac.compare_digest(expected, hash_recebido)


# @csrf_exempt é necessário: webhooks são chamadas server-to-server sem token CSRF.
# A segurança é garantida pela validação HMAC em _validar_assinatura().
@csrf_exempt
def webhook_mercadopago(request):
    if not _validar_assinatura(request):
        return HttpResponse(status=400)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return HttpResponse(status=400)

    payment_id = data.get("data", {}).get("id")

    if not payment_id:
        return HttpResponse(status=400)

    payment_info = sdk.payment().get(payment_id)
    status = payment_info["response"]["status"]

    pagamento = Pagamento.objects.filter(transaction_id=payment_id).first()

    if pagamento and status == "approved":
        pagamento.status = "aprovado"
        pagamento.save()

        pedido = pagamento.pedido
        pedido.status = "pago"
        pedido.save()

        if pedido.usuario:
            carrinho = Carrinho.objects.filter(usuario=pedido.usuario).first()
            if carrinho:
                carrinho.itens.all().delete()

    return HttpResponse(status=200)