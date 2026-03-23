from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Categoria, Produto, ImagemSobre, Avaliacao, ConfiguracaoSobre
from .forms import AvaliacaoForm


def lista_produtos(request):
    produtos = Produto.objects.filter(ativo=True)
    return render(request, 'produtos/lista.html', {'produtos': produtos})


def detalhe_produto(request, id, slug):
    produto = get_object_or_404(
        Produto.objects.prefetch_related('grupos_opcoes__opcoes'),
        id=id,
        slug=slug
    )
    return render(request, 'produtos/detalhe_produto.html', {'produto': produto})


def produtos_por_categoria(request, slug):
    categoria = Categoria.objects.filter(slug=slug).first()

    if categoria:
        produtos = Produto.objects.filter(categoria=categoria, ativo=True)
    else:
        produtos = Produto.objects.none()

    return render(request, 'produtos/lista.html', {
        'produtos': produtos,
        'categoria': categoria,
    })


def home(request):
    canecas = Produto.objects.filter(ativo=True, categoria__slug='canecas')[:8]
    camisas = Produto.objects.filter(ativo=True, categoria__slug='camisas')[:8]
    cadernetas = Produto.objects.filter(ativo=True, categoria__slug='caderneta-de-vacinacao')[:8]

    return render(request, 'home.html', {
        'canecas': canecas,
        'camisas': camisas,
        'cadernetas': cadernetas,
    })


def sobre(request):
    imagens_sobre = ImagemSobre.objects.filter(ativo=True).order_by('-id')[:12]
    avaliacoes    = Avaliacao.objects.filter(aprovado=True)[:12]
    config        = ConfiguracaoSobre.get()

    if request.method == "POST":
        form = AvaliacaoForm(request.POST, request.FILES)
        if form.is_valid():
            avaliacao = form.save(commit=False)
            avaliacao.aprovado = False
            avaliacao.save()
            messages.success(
                request,
                'Avaliação enviada com sucesso! Assim que aprovada, ela aparecerá aqui 💜',
                extra_tags='avaliacao'
            )
            return redirect('sobre')
        else:
            messages.error(
                request,
                'Ops! Verifique os campos e tente novamente.',
                extra_tags='avaliacao'
            )
    else:
        form = AvaliacaoForm()

    return render(request, 'marketing/sobre.html', {
        'imagens_sobre': imagens_sobre,
        'avaliacoes':    avaliacoes,
        'form':          form,
        'config':        config,
    })