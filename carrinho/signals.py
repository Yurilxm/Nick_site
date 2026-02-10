from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import Carrinho, ItemCarrinho
from .services import obter_carrinho


@receiver(user_logged_in)
def associar_carrinho_ao_usuario(sender, request, user, **kwargs):
    carrinho_sessao = obter_carrinho(request)

    # procura carrinho ativo do usuário
    carrinho_usuario = Carrinho.objects.filter(
        usuario=user,
        ativo=True
    ).first()

    # se não existe carrinho antigo → só associa
    if not carrinho_usuario:
        carrinho_sessao.usuario = user
        carrinho_sessao.save()
        return

    # se for o mesmo carrinho, nada a fazer
    if carrinho_sessao.id == carrinho_usuario.id:
        return

    # 👉 mesclar itens
    for item in carrinho_sessao.itens.all():
        item_existente = ItemCarrinho.objects.filter(
            carrinho=carrinho_usuario,
            produto=item.produto
        ).first()

        if item_existente:
            item_existente.quantidade += item.quantidade
            item_existente.save()
            item.delete()
        else:
            item.carrinho = carrinho_usuario
            item.save()

    # desativa carrinho da sessão
    carrinho_sessao.delete()
