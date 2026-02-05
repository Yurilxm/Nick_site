from django.shortcuts import render, redirect
from produtos.models import Produto
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from carrinho.models import ItemCarrinho
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.contrib.auth import login, authenticate, get_user_model
from django.core.mail import send_mail
from django.conf import settings
from .models import LoginCode
from .utils import login_code
from django.utils import timezone


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


def login_email_code_view(request):
    return render(request, "auth/login_email_code.html")


def send_login_code_view(request):
    if request.method == "POST":
        email = request.POST.get("email")

        if not email:
            messages.error(request, "Informe um e-mail válido.")
            return redirect("login")

        # gera código
        code = login_code()

        # salva no banco
        LoginCode.create_code(email=email, code=code)

        # envia email
        send_mail(
            subject="Seu código de acesso | Nick Brindes",
            message=f"Seu código de acesso é: {code}\n\nEle expira em 10 minutos.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        messages.success(
            request,
            "Enviamos um código para o seu e-mail.",
            extra_tags="login-code"
        )

        return redirect("login_code_confirm")

    return redirect("login_code_confirm")



User = get_user_model()


def login_code_confirm_view(request):
    if request.method == "POST":
        code = request.POST.get("code")

        try:
            login_code_obj = LoginCode.objects.get(code=code, used=False)
        except LoginCode.DoesNotExist:
            return render(request, "auth/login_code.html", {
                "error": "Código inválido."
            })

        if not login_code_obj.is_valid():
            return render(request, "auth/login_code.html", {
                "error": "Este código expirou ou já foi utilizado."
            })

        # cria usuário se não existir
        user, created = User.objects.get_or_create(
            email=login_code_obj.email,
            defaults={
                "username": login_code_obj.email
            }
        )

        if created:
            messages.success(request, "Conta criada automaticamente com sucesso! Você já está logado 😊", extra_tags="login")
        else:
            messages.success(request, "Login realizado com sucesso!", extra_tags="login")

        # marca código como usado
        login_code_obj.used = True
        login_code_obj.save()

        # faz login
        login(request, user)

        return redirect("home")

    return render(request, "auth/login_code.html")