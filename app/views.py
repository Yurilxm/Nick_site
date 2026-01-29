from django.shortcuts import render
from produtos.models import Produto
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect


class LoginCustomView(LoginView):
    template_name = 'auth/login.html'

    def form_valid(self, form):
        return super().form_valid(form)

        user = self.request.user
        carrinho_sessao = self.request.session.get('carrinho', {})

        if carrinho_sessao:
            from carrinho.models import ItemCarrinho
            from produtos.models import Produto

            for produto_id, quantidade in carrinho_sessao.items():
                try:
                    produto = Produto.objects.get(id=produto_id)

                    item, criado = ItemCarrinho.objects.get_or_create(
                        usuario=user,
                        produto=produto,
                        defaults={'quantidade': quantidade}
                    )

                    if not criado:
                        item.quantidade += quantidade
                        item.save()

                except Produto.DoesNotExist:
                    pass  # ignora produto inválido

            # limpa sessão depois de migrar
            self.request.session['carrinho'] = {}

        messages.success(self.request, 'Login realizado com sucesso!', extra_tags='login')
        return response

def logout_view(request):
    logout(request)
    messages.info(request, "Logout realizdo com sucesso!", extra_tags='logout')
    return redirect('home')

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

def carrinho_view(request):
    return render(request, 'pages/carrinho.html')