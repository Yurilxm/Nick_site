from django.urls import path
from .views import parcelas_cartao, pedido_confirmado, pagamento, pedido_confirmado, checkout
from .webhooks.mercadopago_webhook import webhook_mercadopago

app_name = "pedidos"

urlpatterns = [
    path("pagamento/", pagamento, name="pagamento"),
    path("webhook/mercadopago/", webhook_mercadopago, name="webhook_mercadopago"),
    path("pedido-confirmado/<int:pedido_id>/", pedido_confirmado, name="pedido_confirmado",),
    path("checkout/<int:pedido_id>/", checkout, name="checkout"),
    path("parcelas-cartao/", parcelas_cartao, name="parcelas_cartao"),
]