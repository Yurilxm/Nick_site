from django.shortcuts import render, get_object_or_404
from .models import Produto

def lista_produtos(request):
    produtos = Produto.objects.all()
    return render(request, 'produtos/lista.html', {'produtos': produtos})

def detalhe_produto(request, id):
    produto = get_object_or_404(Produto, id=id)
    return render(request, 'produtos/detalhe.html', {'produto': produto})