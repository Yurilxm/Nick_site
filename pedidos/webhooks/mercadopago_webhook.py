import json
import mercadopago
from django.http import HttpResponse
from django.conf import settings

from pedidos.models import Pagamento

sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)


def webhook_mercadopago(request):

    data = json.loads(request.body)

    payment_id = data.get("data", {}).get("id")

    if not payment_id:
        return HttpResponse(status=400)

    payment_info = sdk.payment().get(payment_id)

    status = payment_info["response"]["status"]

    pagamento = Pagamento.objects.filter(
        transaction_id=payment_id
    ).first()

    if pagamento:

        if status == "approved":

            pagamento.status = "aprovado"
            pagamento.save()

            pedido = pagamento.pedido

            pedido.status = "pago"
            pedido.save()

    return HttpResponse(status=200)