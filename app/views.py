from django.shortcuts import render
from produtos.models import Produto
# from django.contrib.auth.decorators import login_required


def home_view(request):
    canecas = Produto.objects.filter(
        categoria__slug='canecas'
    ).order_by('-id')[:8]

    agendas = Produto.objects.filter(
        categoria__slug='agendas'
    ).order_by('-id')[:8]

    cadernetas = Produto.objects.filter(
        categoria__slug='cadernetas'
    ).order_by('-id')[:8]

    context = {
        'canecas': canecas,
        'agendas': agendas,
        'cadernetas': cadernetas,
    }

    return render(request, 'pages/home.html', context)


def cadernetas_view(request):
    return render(request, 'pages/cadernetas.html')

def sobre_view(request):
    return render(request, 'pages/sobre.html')

def contato_view(request):
    return render(request, 'pages/contato.html')

def login_view(request):
    return render(request, 'pages/login.html')

def carrinho_view(request):
    return render(request, 'pages/carrinho.html')