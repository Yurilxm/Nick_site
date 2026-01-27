from .models import Carrinho


def obter_carrinho(request):
    """
    Retorna o carrinho ativo do usuário ou da sessão.
    Cria um novo se não existir.
    """
    if request.user.is_authenticated:
        carrinho, created = Carrinho.objects.get_or_create(
            usuario=request.user,
            ativo=True
        )
        return carrinho

    carrinho_id = request.session.get('carrinho_id')

    if carrinho_id:
        carrinho = Carrinho.objects.filter(
            id=carrinho_id,
            ativo=True,
            usuario__isnull=True
        ).first()

        if carrinho:
            return carrinho

    carrinho = Carrinho.objects.create()
    request.session['carrinho_id'] = carrinho.id
    return carrinho