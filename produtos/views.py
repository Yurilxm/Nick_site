from django.shortcuts import render, get_object_or_404
from .models import Categoria, Produto

def lista_produtos(request):
    produtos = Produto.objects.filter(ativo=True)
    return render(request, 'produtos/lista.html', {'produtos': produtos})

def detalhe_produto(request, id, slug):
    produto = get_object_or_404(Produto, id=id, slug=slug)
    return render(request, 'produtos/detalhe_produto.html', {'produto': produto})

def produtos_por_categoria(request, slug):
    categoria = get_object_or_404(Categoria, slug=slug)
    produtos = Produto.objects.filter(categoria=categoria)
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
