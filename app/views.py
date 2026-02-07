from django.shortcuts import render, redirect
from produtos.models import Produto
from django.contrib.auth.views import (LoginView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView,)
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth import logout, login, authenticate, get_user_model
from django.views.decorators.http import require_POST, require_GET
from django.http import JsonResponse
from carrinho.models import ItemCarrinho
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from .models import LoginCode
from .utils import login_code

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

        self.request.session['carrinho'] = {}

        messages.success(self.request, 'Login realizado com sucesso!', extra_tags='login')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'E-mail ou senha incorretos. Tente novamente.', extra_tags='error')
        return super().form_invalid(form)


@require_POST
def register_view(request):
    email = request.POST.get('email')
    password1 = request.POST.get('password1')
    password2 = request.POST.get('password2')

    if not email or not password1 or not password2:
        messages.error(request, 'Preencha todos os campos.', extra_tags='error')
        return redirect('login')

    if password1 != password2:
        messages.error(request, 'As senhas não coincidem.', extra_tags='error')
        return redirect('login')

    if len(password1) < 8:
        messages.error(
            request,
            'A senha deve conter pelo menos 8 caracteres.',
            extra_tags='error'
        )
        return redirect('login')

    if User.objects.filter(username=email).exists():
        messages.error(request, 'Este e-mail já está cadastrado.', extra_tags='error')
        return redirect('login')

    user = User.objects.create_user(
        username=email,
        email=email,
        password=password1
    )

    user = authenticate(username=email, password=password1)
    if user:
        login(request, user)

    messages.success(request, 'Conta criada com sucesso! Você já está logado 😊', extra_tags='success')
    return redirect('home')


def logout_view(request):
    logout(request)
    messages.info(request, 'Logout realizado com sucesso!', extra_tags='logout')
    return redirect('home')


def home_view(request):
    canecas = Produto.objects.filter(categoria__slug='canecas').order_by('-id')[:8]
    agendas = Produto.objects.filter(categoria__slug='agendas').order_by('-id')[:8]
    cadernetas = Produto.objects.filter(categoria__slug='cadernetas').order_by('-id')[:8]

    return render(request, 'pages/home.html', {
        'canecas': canecas,
        'agendas': agendas,
        'cadernetas': cadernetas,
    })


def cadernetas_view(request):
    return render(request, 'pages/cadernetas.html')


def sobre_view(request):
    return render(request, 'pages/sobre.html')


def contato_view(request):
    return render(request, 'pages/contato.html')


def carrinho_view(request):
    return render(request, 'pages/carrinho.html')


def login_email_code_view(request):
    return render(request, 'auth/login_email_code.html')


def send_login_code_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        if not email:
            messages.error(request, 'Informe um e-mail válido.', extra_tags='error')
            return redirect('login')

        code = login_code()
        LoginCode.create_code(email=email, code=code)

        send_mail(
            subject='Seu código de acesso | Nick Brindes',
            message=f'Seu código de acesso é: {code}\n\nEle expira em 10 minutos.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        messages.success(
            request,
            'Se existir uma conta com esse e-mail, você receberá um código de acesso.',
            extra_tags='login-code'
        )

        return redirect('login_code_confirm')

    return redirect('login')


User = get_user_model()


def login_code_confirm_view(request):
    if request.method == 'POST':
        code = request.POST.get('code')

        try:
            login_code_obj = LoginCode.objects.get(code=code, used=False)
        except LoginCode.DoesNotExist:
            messages.error(request, 'Código inválido.', extra_tags='error')
            return redirect('login_code_confirm')

        if not login_code_obj.is_valid():
            messages.error(request, 'Este código expirou ou já foi utilizado.', extra_tags='error')
            return redirect('login_code_confirm')

        user, created = User.objects.get_or_create(
            email=login_code_obj.email,
            defaults={'username': login_code_obj.email}
        )

        login_code_obj.used = True
        login_code_obj.save()

        login(request, user)

        if created:
            messages.success(request, 'Conta criada automaticamente com sucesso! Você já está logado 😊', extra_tags='login')
        else:
            messages.success(request, 'Login realizado com sucesso!', extra_tags='login')

        return redirect('home')

    return render(request, 'auth/login_code.html')


# =========================
# 🔐 RESET DE SENHA (CUSTOM)
# =========================
class PasswordResetCustomView(PasswordResetView):
    template_name = 'auth/password_reset.html'
    success_url = reverse_lazy('password_reset_done')

    def form_valid(self, form):
        messages.success(
            self.request,
            'Se existir uma conta com esse e-mail, você receberá instruções para redefinir sua senha.',
            extra_tags='success'
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Informe um e-mail válido.', extra_tags='error')
        return super().form_invalid(form)


class PasswordResetDoneCustomView(PasswordResetDoneView):
    template_name = 'auth/password_reset_done.html'


class PasswordResetConfirmCustomView(PasswordResetConfirmView):
    template_name = 'auth/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

    def form_invalid(self, form):
        for errors in form.errors.values():
            for error in errors:
                messages.error(self.request, error, extra_tags='error')
        return super().form_invalid(form)

    def form_valid(self, form):
        messages.success(
            self.request,
            'Senha redefinida com sucesso! Faça login com sua nova senha.',
            extra_tags='success'
        )
        return super().form_valid(form)


class PasswordResetCompleteCustomView(PasswordResetCompleteView):
    template_name = 'auth/password_reset_complete.html'




@require_GET
def search_products_view(request):
    query = request.GET.get('q', '').strip()

    if not query:
        return JsonResponse({'results': []})

    produtos = Produto.objects.filter(
        nome__icontains=query
    )[:5]

    results = [
        {
            'id': produto.id,
            'nome': produto.nome,
            'slug': produto.slug,
            'imagem': produto.imagem.url if produto.imagem else '',
            'preco': str(produto.preco),
        }
        for produto in produtos
    ]

    return JsonResponse({'results': results})