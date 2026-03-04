from django.shortcuts import render, get_object_or_404
from .models import Categoria, Produto

def lista_produtos(request):
    produtos = Produto.objects.filter(ativo=True)
    return render(request, 'produtos/lista.html', {'produtos': produtos})

def detalhe_produto(request, id, slug):
    produto = get_object_or_404(Produto.objects.prefetch_related('grupos_opcoes__opcoes'), id=id, slug=slug)
    return render(request, 'produtos/detalhe_produto.html', {'produto': produto})

def produtos_por_categoria(request, slug):
    categoria = Categoria.objects.filter(slug=slug).first()

    if categoria:
        produtos = Produto.objects.filter(
            categoria=categoria,
            ativo=True
        )
    else:
        produtos = Produto.objects.none()  # QuerySet vazio

    return render(request, 'produtos/lista.html', {
        'produtos': produtos,
        'categoria': categoria
    })

def home(request):
    canecas = Produto.objects.filter(
        ativo=True,
        categoria__slug='canecas'
    )[:8]

    camisas = Produto.objects.filter(
        ativo=True,
        categoria__slug='camisas'
    )[:8]

    cadernetas = Produto.objects.filter(
        ativo=True,
        categoria__slug='caderneta-de-vacinacao'
    )[:8]

    context = {
        'canecas': canecas,
        'camisas': camisas,
        'cadernetas': cadernetas,
    }

    return render(request, 'home.html', context)
