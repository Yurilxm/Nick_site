def validar_pedido(pedido):

    if pedido.total > 10000:
        return False

    #if pedido.usuario and pedido.usuario.is_staff:
    #    return False

    return True