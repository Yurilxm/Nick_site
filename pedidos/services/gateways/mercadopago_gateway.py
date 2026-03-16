import mercadopago
from django.conf import settings

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
        payment = sdk.payment().create(payment_data)
        print("DEBUG PIX:", payment)
        return payment.get("response", {})

    def criar_cartao(self, pedido, token, parcelas, payment_method_id):
        payment_data = {
            "transaction_amount": float(pedido.total),
            "token": token,
            "installments": int(parcelas),
            "payment_method_id": payment_method_id,  # ex: "visa", "master"
            "description": f"Pedido {pedido.id}",
            "payer": {
                "email": pedido.usuario.email
            }
        }
        payment = sdk.payment().create(payment_data)
        print("DEBUG CARTÃO:", payment)
        return payment.get("response", {})

    def criar_boleto(self, pedido):
        payment_data = {
            "transaction_amount": float(pedido.total),
            "payment_method_id": "bolbradesco",
            "description": f"Pedido {pedido.id}",
            "payer": {
                "email": pedido.usuario.email,
                "first_name": pedido.usuario.first_name or "Cliente",
                "last_name": pedido.usuario.last_name or "Nick Brindes",
                "identification": {
                    "type": "CPF",
                    "number": "19119119100"
                },
                "address": {
                    "zip_code": pedido.cep_entrega or "01310100",
                    "street_name": pedido.rua or "Av Paulista",
                    "street_number": pedido.numero or "1000",
                    "neighborhood": pedido.bairro or "Bela Vista",
                    "city": pedido.cidade or "São Paulo",
                    "federal_unit": pedido.estado or "SP"
                }
            }
        }
        payment = sdk.payment().create(payment_data)
        print("DEBUG BOLETO:", payment)
        return payment.get("response", {})