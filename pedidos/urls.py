from django.urls import path
from .views import pedido_confirmado

urlpatterns = [
    path(
        "pedido-confirmado/<int:pedido_id>/", pedido_confirmado, name="pedido_confirmado",
    ),
]