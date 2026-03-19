from django.utils import timezone
from datetime import timedelta


def validar_pedido(pedido):

    # 1. Pedido com valor muito alto
    if pedido.total > 10000:
        return False

    # 2. Bloqueia admins/staff (descomentado antes do deploy)
    # if pedido.usuario and pedido.usuario.is_staff:
    #     return False

    # 3. Pedido com valor zerado ou negativo
    if pedido.total <= 0:
        return False

    # 4. Pedido sem itens
    if not pedido.itens.exists():
        return False

    # 5. Usuário sem e-mail
    if not pedido.usuario or not pedido.usuario.email:
        return False

    # 6. Muitos pedidos em pouco tempo (anti-spam)
    from pedidos.models import Pedido
    um_minuto_atras = timezone.now() - timedelta(minutes=1)
    pedidos_recentes = Pedido.objects.filter(
        usuario=pedido.usuario,
        criado_em__gte=um_minuto_atras
    ).exclude(id=pedido.id).count()

    if pedidos_recentes >= 3:
        return False

    return True