from pedidos.models import Pagamento
from .gateways.mercadopago_gateway import MercadoPagoGateway

gateway = MercadoPagoGateway()

def pedido_ja_tem_pagamento_pendente(pedido):
    return Pagamento.objects.filter(
        pedido=pedido,
        status="pendente"
    ).exists()

def criar_pagamento_pix(pedido, valor=None):
    """
    Cria pagamento PIX.
    Se 'valor' for passado, usa esse valor; caso contrário, usa pedido.total.
    """
    if pedido_ja_tem_pagamento_pendente(pedido):
        return Pagamento.objects.filter(
            pedido=pedido,
            status="pendente"
        ).first()

    # Se valor não foi informado, usa o total do pedido
    if valor is None:
        valor = pedido.total

    # Cria o pagamento no gateway com o valor (que já pode ter desconto)
    response = gateway.criar_pix(pedido, valor=float(valor))  # supondo que o gateway aceite um parâmetro valor

    payment_id = response.get("id")
    qr_code = response.get("point_of_interaction", {}).get("transaction_data", {}).get("qr_code")
    qr_code_base64 = response.get("point_of_interaction", {}).get("transaction_data", {}).get("qr_code_base64")

    if not payment_id:
        raise ValueError(f"Erro ao criar pagamento PIX: ID do pagamento não retornado. Response: {response}")

    pagamento = Pagamento.objects.create(
        pedido=pedido,
        metodo="pix",
        transaction_id=payment_id,
        qr_code=qr_code,
        qr_code_base64=qr_code_base64
    )
    return pagamento

def criar_pagamento_boleto(pedido):
    response = gateway.criar_boleto(pedido)
    payment_id = response.get("id")
    boleto_url = response.get("transaction_details", {}).get("external_resource_url")

    if not payment_id:
        raise ValueError(f"Erro ao criar pagamento boleto. Response: {response}")

    pagamento = Pagamento.objects.create(
        pedido=pedido,
        metodo="boleto",
        transaction_id=payment_id,
        boleto_url=boleto_url
    )
    return pagamento

def criar_pagamento_cartao(pedido, token, parcelas, bandeira):
    response = gateway.criar_cartao(pedido, token, parcelas, bandeira)
    payment_id = response.get("id")
    status = response.get("status", "pendente")

    if not payment_id:
        raise ValueError(f"Erro ao criar pagamento cartão. Response: {response}")

    pagamento = Pagamento.objects.create(
        pedido=pedido,
        metodo="cartao",
        transaction_id=payment_id,
        status="aprovado" if status == "approved" else status
    )
    return pagamento