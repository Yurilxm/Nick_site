from carrinho.models import Carrinho, ItemCarrinho

def obter_carrinho(request):
    """
    Retorna o carrinho ativo do usuário ou da sessão.
    Se o usuário acabou de logar e tinha carrinho anônimo,
    os itens são migrados automaticamente.
    """

    carrinho_sessao_id = request.session.get('carrinho_id')
    carrinho_sessao = None

    # 👉 pega carrinho anônimo da sessão
    if carrinho_sessao_id:
        carrinho_sessao = Carrinho.objects.filter(
            id=carrinho_sessao_id,
            ativo=True,
            usuario__isnull=True
        ).first()

    # 👉 usuário logado
    if request.user.is_authenticated:

        carrinho_usuario, created = Carrinho.objects.get_or_create(
            usuario=request.user,
            ativo=True
        )

        # 🔥 MIGRA itens do carrinho anônimo
        if carrinho_sessao and carrinho_sessao != carrinho_usuario:

            for item in carrinho_sessao.itens.all():
                item_existente = carrinho_usuario.itens.filter(
                    produto=item.produto
                ).first()

                if item_existente:
                    item_existente.quantidade += item.quantidade
                    item_existente.save()
                else:
                    item.carrinho = carrinho_usuario
                    item.save()

            carrinho_sessao.delete()
            request.session.pop('carrinho_id', None)

        return carrinho_usuario

    # 👉 usuário anônimo
    if carrinho_sessao:
        return carrinho_sessao

    carrinho = Carrinho.objects.create()
    request.session['carrinho_id'] = carrinho.id
    return carrinho