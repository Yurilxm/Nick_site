from pedidos.models import Pagamento
from .gateways.mercadopago_gateway import MercadoPagoGateway
from django.utils.dateparse import parse_datetime

gateway = MercadoPagoGateway()


def pedido_ja_tem_pagamento_pendente(pedido):

    return Pagamento.objects.filter(
        pedido=pedido,
        status="pendente"
    ).exists()



def criar_pagamento_pix(pedido):

    if pedido_ja_tem_pagamento_pendente(pedido):
        return Pagamento.objects.filter(
            pedido=pedido,
            status="pendente"
        ).first()

    response = gateway.criar_pix(pedido)

    pagamento = Pagamento.objects.create(
        pedido=pedido,
        metodo="pix",
        transaction_id=response["id"],
        qr_code=response["point_of_interaction"]["transaction_data"]["qr_code"],
        qr_code_base64=response["point_of_interaction"]["transaction_data"]["qr_code_base64"]
    )

    return pagamento


def criar_pagamento_boleto(pedido):

    response = gateway.criar_boleto(pedido)

    pagamento = Pagamento.objects.create(
        pedido=pedido,
        metodo="boleto",
        transaction_id=response["id"],
        boleto_url=response["transaction_details"]["external_resource_url"]
    )

    return pagamento


def criar_pagamento_cartao(pedido, token, parcelas):

    response = gateway.criar_cartao(pedido, token, parcelas)

    pagamento = Pagamento.objects.create(
        pedido=pedido,
        metodo="cartao",
        transaction_id=response["id"],
        status=response["status"]
    )

    return pagamento