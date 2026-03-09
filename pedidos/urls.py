from django.urls import path
from .views import pedido_confirmado, pagamento

app_name = "pedidos"

urlpatterns = [
    path("pagamento/", pagamento, name="pagamento"),
    path("pedido-confirmado/<int:pedido_id>/", pedido_confirmado, name="pedido_confirmado",),
]