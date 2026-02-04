from django.shortcuts import render, redirect
from produtos.models import Produto
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from carrinho.models import ItemCarrinho
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.contrib.auth import login, authenticate


class LoginCustomView(LoginView):
    template_name = 'auth/login.html'

    def form_valid(self, form):
        response = super().form_valid(form)

        user = self.request.user
        carrinho_sessao = self.request.session.get('carrinho', {})


        for produto_id, quantidade in carrinho_sessao.items():
            item, created = ItemCarrinho.objects.get_or_create(
                usuario=user,
                produto_id=produto_id,
                defaults={'quantidade': quantidade}
            )

            if not created:
                item.quantidade += quantidade
                item.save()

        # limpa sessão depois de migrar
        self.request.session['carrinho'] = {}

        messages.success(self.request, 'Login realizado com sucesso!', extra_tags='login')
        
        return response
    
    def form_invalid(self, form):
        messages.error(
            self.request,
            'E-mail ou senha incorretos. Tente novamente.',
            extra_tags='error'
        )
        return super().form_invalid(form)
    
    
@require_POST
def register_view(request):
    email = request.POST.get('email')
    password1 = request.POST.get('password1')
    password2 = request.POST.get('password2')

    # Senhas diferentes
    if password1 != password2:
        messages.error(
            request,
            'As senhas não coincidem.',
            extra_tags='error'
        )
        return redirect('login')

    # Email já cadastrado
    if User.objects.filter(username=email).exists():
        messages.error(
            request,
            'Este e-mail já está cadastrado.',
            extra_tags='error'
        )
        return redirect('login')

    # Cria o usuário
    user = User.objects.create_user(
        username=email,
        email=email,
        password=password1
    )

    # 🔐 AUTOLOGIN
    user = authenticate(username=email, password=password1)
    if user:
        login(request, user)

    messages.success(
        request,
        'Conta criada com sucesso! Você já está logado 😊',
        extra_tags='success'
    )

    return redirect('home')


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