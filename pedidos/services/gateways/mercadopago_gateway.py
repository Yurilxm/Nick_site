import mercadopago
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)


class MercadoPagoGateway:

    def criar_pix(self, pedido):
        payment_data = {
            "transaction_amount": float(pedido.total),
            "payment_method_id": "pix",
            "description": f"Pedido {pedido.id}",
            "notification_url": f"{settings.SITE_URL}/pedidos/webhook/mercadopago/",
            "payer": {
                "email": pedido.usuario.email
            }
        }

        try:
            payment = sdk.payment().create(payment_data)
            return payment.get("response", {})
        except Exception as e:
            logger.error(f"Erro ao criar PIX: {e}")
            return {}

    def criar_cartao(self, pedido, token, parcelas, payment_method_id):
        payment_data = {
            "transaction_amount": float(pedido.total),
            "token": token,
            "installments": int(parcelas),
            "payment_method_id": payment_method_id,
            "description": f"Pedido {pedido.id}",
            "payer": {
                "email": pedido.usuario.email
            }
        }

        try:
            payment = sdk.payment().create(payment_data)
            return payment.get("response", {})
        except Exception as e:
            logger.error(f"Erro ao criar pagamento com cartão: {e}")
            return {}

    def criar_boleto(self, pedido):
        payment_data = {
            "transaction_amount": float(pedido.total),
            "payment_method_id": "bolbradesco",
            "description": f"Pedido {pedido.id}",
            "payer": {
                "email": pedido.usuario.email,
                "first_name": pedido.usuario.first_name or "Cliente",
                "last_name": pedido.usuario.last_name or "Cliente",
                "identification": {
                    "type": "CPF",
                    "number": "19119119100"  # depois podemos melhorar isso
                },
                "address": {
                    "zip_code": pedido.cep_entrega or "00000000",
                    "street_name": pedido.rua or "Não informado",
                    "street_number": pedido.numero or "0",
                    "neighborhood": pedido.bairro or "Não informado",
                    "city": pedido.cidade or "Não informado",
                    "federal_unit": pedido.estado or "SP"
                }
            }
        }

        try:
            payment = sdk.payment().create(payment_data)
            return payment.get("response", {})
        except Exception as e:
            logger.error(f"Erro ao criar boleto: {e}")
            return {}