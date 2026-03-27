import mercadopago
import logging
from django.conf import settings
from decimal import Decimal, ROUND_HALF_UP

logger = logging.getLogger(__name__)

sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)


def _extrair_nome(pedido):
    """Extrai nome e sobrenome. Prioriza o campo nome_cliente do pedido."""

    if pedido.nome_cliente:
        nome = pedido.nome_cliente.strip()
        partes = nome.split()
        first_name = partes[0]
        last_name = " ".join(partes[1:]) if len(partes) > 1 else "Cliente"
        return first_name, last_name

    nome = pedido.usuario.get_full_name().strip()
    if nome:
        partes = nome.split()
        first_name = partes[0]
        last_name = " ".join(partes[1:]) if len(partes) > 1 else "Cliente"
    else:
        first_name = "Cliente"
        last_name = "Cliente"

    return first_name, last_name


def _cpf_numerico(cpf):
    return (cpf or "").replace(".", "").replace("-", "").strip()


class MercadoPagoGateway:

    def _formatar_valor(self, valor):
        """Garante valor com 2 casas decimais (padrão seguro)"""
        return Decimal(valor).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # =====================================
    # PIX
    # =====================================
    def criar_pix(self, pedido, valor=None):
        if valor is None:
            valor = pedido.total

        valor = self._formatar_valor(valor)

        payer = {
            "email": pedido.usuario.email,
        }

        # CPF opcional no PIX
        if pedido.cpf:
            payer["identification"] = {
                "type": "CPF",
                "number": _cpf_numerico(pedido.cpf),
            }

        payment_data = {
            "transaction_amount": float(valor),
            "payment_method_id": "pix",
            "description": f"Pedido {pedido.id}",
            "notification_url": f"{settings.SITE_URL}/pedidos/webhook/mercadopago/",
            "payer": payer,
        }

        print("VALOR FINAL PIX:", valor)

        try:
            payment = sdk.payment().create(payment_data)
            return payment.get("response", {})
        except Exception as e:
            logger.error(f"Erro ao criar PIX para pedido {pedido.id}: {e}")
            return {}

    # =====================================
    # CARTÃO
    # =====================================
    def criar_cartao(self, pedido, token, parcelas, payment_method_id):
        valor = self._formatar_valor(pedido.total)

        payment_data = {
            "transaction_amount": float(valor),
            "token": token,
            "installments": int(parcelas),
            "payment_method_id": payment_method_id,
            "description": f"Pedido {pedido.id}",
            "payer": {
                "email": pedido.usuario.email,
                "identification": {
                    "type": "CPF",
                    "number": _cpf_numerico(pedido.cpf),
                },
            },
        }

        try:
            payment = sdk.payment().create(payment_data)
            return payment.get("response", {})
        except Exception as e:
            logger.error(f"Erro ao criar pagamento com cartão para pedido {pedido.id}: {e}")
            return {}

    # =====================================
    # BOLETO
    # =====================================
    def criar_boleto(self, pedido):
        first_name, last_name = _extrair_nome(pedido)
        valor = self._formatar_valor(pedido.total)

        payment_data = {
            "transaction_amount": float(valor),
            "payment_method_id": "bolbradesco",
            "description": f"Pedido {pedido.id}",
            "payer": {
                "email": pedido.usuario.email,
                "first_name": first_name,
                "last_name": last_name,
                "identification": {
                    "type": "CPF",
                    "number": _cpf_numerico(pedido.cpf),
                },
                "address": {
                    "zip_code": pedido.cep_entrega or "00000000",
                    "street_name": pedido.rua or "Não informado",
                    "street_number": pedido.numero or "0",
                    "neighborhood": pedido.bairro or "Não informado",
                    "city": pedido.cidade or "Não informado",
                    "federal_unit": pedido.estado or "SP",
                },
            },
        }

        try:
            payment = sdk.payment().create(payment_data)
            return payment.get("response", {})
        except Exception as e:
            logger.error(f"Erro ao criar boleto para pedido {pedido.id}: {e}")
            return {}