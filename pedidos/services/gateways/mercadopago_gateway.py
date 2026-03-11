import mercadopago
from django.conf import settings

print("TOKEN CARREGADO:", settings.MERCADO_PAGO_ACCESS_TOKEN[:20])

sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

class MercadoPagoGateway:

    def criar_pix(self, pedido):
        payment_data = {
            "transaction_amount": float(pedido.total),
            "payment_method_id": "pix",
            "description": f"Pedido {pedido.id}",
            "payer": {
                "email": pedido.usuario.email if hasattr(pedido, "usuario") else "cliente@exemplo.com"
            }
        }

        payment = sdk.payment().create(payment_data)
        # Retorna o response completo do SDK
        return payment.get("response", {})

    def criar_cartao(self, pedido, token, parcelas):
        payment_data = {
            "transaction_amount": float(pedido.total),
            "token": token,
            "installments": int(parcelas),
            "payment_method_id": "credit_card",
            "description": f"Pedido {pedido.id}",
            "payer": {
                "email": pedido.usuario.email if hasattr(pedido, "usuario") else "cliente@exemplo.com"
            }
        }
        payment = sdk.payment().create(payment_data)
        return payment.get("response", {})

    def criar_boleto(self, pedido):
        payment_data = {
            "transaction_amount": float(pedido.total),
            "payment_method_id": "bolbradesco",
            "description": f"Pedido {pedido.id}",
            "payer": {
                "email": pedido.usuario.email if hasattr(pedido, "usuario") else "cliente@exemplo.com"
            }
        }
        payment = sdk.payment().create(payment_data)
        return payment.get("response", {})