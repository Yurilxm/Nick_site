from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


def validar_pedido(pedido):
    """Versão original que retorna apenas booleano"""
    valido, _ = validar_pedido_com_motivo(pedido)
    return valido


def validar_pedido_com_motivo(pedido):
    """
    Valida um pedido contra critérios de antifraude.
    Retorna (True, None) se válido, ou (False, motivo) caso contrário.
    """
    # 1. Pedido com valor muito alto
    if pedido.total > 10000:
        motivo = f"valor total R$ {pedido.total} é maior que R$ 10.000,00"
        logger.warning(f"Pedido {pedido.id} bloqueado: {motivo}")
        return False, motivo

    # 2. Bloqueia admins/staff
    if pedido.usuario and pedido.usuario.is_staff:
        motivo = "usuário é administrador/staff"
        logger.warning(f"Pedido {pedido.id} bloqueado: {motivo}")
        return False, motivo

    # 3. Pedido com valor zerado ou negativo
    if pedido.total <= 0:
        motivo = f"valor total R$ {pedido.total} é inválido (zero ou negativo)"
        logger.warning(f"Pedido {pedido.id} bloqueado: {motivo}")
        return False, motivo

    # 4. Pedido sem itens
    if not pedido.itens.exists():
        motivo = "pedido não possui itens"
        logger.warning(f"Pedido {pedido.id} bloqueado: {motivo}")
        return False, motivo

    # 5. Usuário sem e-mail
    if not pedido.usuario or not pedido.usuario.email:
        motivo = "usuário não possui e-mail cadastrado"
        logger.warning(f"Pedido {pedido.id} bloqueado: {motivo}")
        return False, motivo

    # 6. Muitos pedidos em pouco tempo (anti-spam)
    from pedidos.models import Pedido
    um_minuto_atras = timezone.now() - timedelta(minutes=1)
    pedidos_recentes = Pedido.objects.filter(
        usuario=pedido.usuario,
        criado_em__gte=um_minuto_atras
    ).exclude(id=pedido.id).count()

    if pedidos_recentes >= 3:
        motivo = f"usuário fez {pedidos_recentes} pedidos no último minuto"
        logger.warning(f"Pedido {pedido.id} bloqueado: {motivo}")
        return False, motivo

    logger.info(f"Pedido {pedido.id} passou na validação de antifraude")
    return True, None