from django.urls import path
from .views import (parcelas_cartao, pedido_confirmado, pagamento, meus_pedidos, verificar_pagamento, pedido_detalhe)
from .webhooks.mercadopago_webhook import webhook_mercadopago
from .pdf import gerar_ficha_pdf

app_name = "pedidos"

urlpatterns = [
    path("pagamento/", pagamento, name="pagamento"),
    path("admin/pedido/<int:pedido_id>/pdf/", gerar_ficha_pdf, name="pedido_pdf"),
    path("webhook/mercadopago/", webhook_mercadopago, name="webhook_mercadopago"),
    path("pedido-confirmado/<int:pedido_id>/", pedido_confirmado, name="pedido_confirmado"),
    path("parcelas-cartao/", parcelas_cartao, name="parcelas_cartao"),
    path("meus-pedidos/", meus_pedidos, name="meus_pedidos"),
    path("verificar-pagamento/<int:pedido_id>/", verificar_pagamento, name="verificar_pagamento"),
    path("pedido/<int:pedido_id>/", pedido_detalhe, name="pedido_detalhe"),
]