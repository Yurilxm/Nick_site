import mercadopago, uuid
from django.conf import settings
from datetime import datetime, timedelta, timezone

sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)


class MercadoPagoGateway:

    def criar_pix(self, pedido):

        payment_data = {
            "transaction_amount": float(pedido.total),
            "payment_method_id": "pix",
            "description": f"Pedido {pedido.id}",
        }

        headers = {
            "X-Idempotency-Key": str(uuid.uuid4())
        }

        payment = sdk.payment().create(
            payment_data,
            request_options={"headers": headers}
        )

        return payment["response"]

    def criar_cartao(self, pedido, token, parcelas):

        payment_data = {
            "transaction_amount": float(pedido.total),
            "token": token,
            "installments": int(parcelas),
            "description": f"Pedido {pedido.id}",
        }

        payment = sdk.payment().create(payment_data)

        return payment["response"]

    def criar_boleto(self, pedido):

        payment_data = {
            "transaction_amount": float(pedido.total),
            "payment_method_id": "bolbradesco",
            "description": f"Pedido {pedido.id}",
        }

        payment = sdk.payment().create(payment_data)

        return payment["response"]