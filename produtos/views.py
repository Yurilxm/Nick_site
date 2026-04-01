from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Categoria, Produto, ImagemSobre, Avaliacao, ConfiguracaoSobre
from .forms import AvaliacaoForm


def lista_produtos(request):
    produtos_list = Produto.objects.filter(ativo=True).prefetch_related("categoria")

    paginator = Paginator(produtos_list, 16)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'produtos/lista.html', {
        'produtos': page_obj,
        'page_obj': page_obj,
    })


def detalhe_produto(request, produto_id, slug):
    produto = get_object_or_404(
        Produto.objects.prefetch_related('grupos_opcoes__opcoes', 'categoria'),
        id=produto_id,
        slug=slug
    )
    return render(request, 'produtos/detalhe_produto.html', {'produto': produto})


def produtos_por_categoria(request, slug):
    categoria = Categoria.objects.filter(slug=slug).first()

    if categoria:
        produtos_list = Produto.objects.filter(
            categoria=categoria,
            ativo=True
        ).prefetch_related("categoria")
    else:
        produtos_list = Produto.objects.none()

    paginator = Paginator(produtos_list, 16)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'produtos/lista.html', {
        'produtos': page_obj,
        'page_obj': page_obj,
        'categoria': categoria,
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