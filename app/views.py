# 🔹 Python padrão
from django.utils import timezone
import requests

# 🔹 Django - Core / Utilidades
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_POST, require_GET
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

# 🔹 Django - Autenticação
from django.contrib.auth import (
    login, logout, authenticate, get_user_model
)
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# 🔹 Django - Views de autenticação (reset de senha)
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView,
)

# 🔹 Django - Email / Templates
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

# 🔹 Apps internos
from produtos.models import Produto
from carrinho.models import ItemCarrinho
from .models import UserProfile, LoginCode, EmailVerificationToken
from .forms import RegisterForm, LoginForm
from .utils import login_code

from django.utils.http import url_has_allowed_host_and_scheme


# =========================
# LOGIN + CADASTRO
# =========================
def login_view(request):
    next_url = request.GET.get('next', '')
    if next_url:
        request.session['next_url'] = next_url
    form_login = LoginForm()
    form_register = RegisterForm()
    active_tab = 'login'

    if request.method == 'POST':
        if 'login_submit' in request.POST:
            form_login = LoginForm(request, data=request.POST)
            if form_login.is_valid():
                user = form_login.get_user()

                profile = user.profile
                if not profile.email_verified:
                    request.session['user_id'] = user.id
                    messages.warning(request, 'Por favor, verifique seu e-mail antes de fazer login.', extra_tags='warning')
                    return redirect('verification_email')

                login(request, user)

                # ✅ CORRIGIDO: usar cleaned_data após form.is_valid()
                if form_login.cleaned_data.get('remember'):
                    request.session.set_expiry(settings.SESSION_COOKIE_AGE)
                else:
                    request.session.set_expiry(0)

                carrinho_sessao = request.session.get('carrinho', {})
                for produto_id, quantidade in carrinho_sessao.items():
                    item, created = ItemCarrinho.objects.get_or_create(
                        usuario=user,
                        produto_id=produto_id,
                        defaults={'quantidade': quantidade}
                    )
                    if not created:
                        item.quantidade += quantidade
                        item.save()
                request.session['carrinho'] = {}

                messages.success(request, 'Login realizado com sucesso!', extra_tags='login')
                redirect_url = request.session.pop('next_url', next_url or 'home')
                return redirect(redirect_url)
            else:
                active_tab = 'login'
                form_register = RegisterForm()

        elif 'register_submit' in request.POST:
            form_register = RegisterForm(request.POST)
            if form_register.is_valid():
                data = form_register.cleaned_data

                user = User.objects.create_user(
                    username=data['email'],
                    email=data['email'],
                    password=data['password1'],
                    first_name=data['nome'].split()[0] if data['nome'] else ''
                )

                request.session['user_id'] = user.id

                profile = user.profile
                profile.nome_completo = data['nome']
                profile.save()

                send_verification_email(request, user)

                messages.success(
                    request,
                    'Conta criada com sucesso! Verifique seu e-mail para confirmar o cadastro.',
                    extra_tags='success'
                )
                return redirect('verification_email')
            else:
                active_tab = 'register'
                form_login = LoginForm()

    return render(request, 'auth/login.html', {
        'form_login': form_login,
        'form_register': form_register,
        'next': next_url,
        'active_tab': active_tab,
    })


def send_verification_email(request, user):
    token = EmailVerificationToken.create_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    verification_link = request.build_absolute_uri(
        reverse('verify_email', kwargs={'uidb64': uid, 'token': token.token})
    )
    context = {
        'user': user,
        'verification_link': verification_link,
        'site_name': 'Mimos da Nick',
    }
    html_content = render_to_string('emails/verify_email.html', context)
    text_content = render_to_string('emails/verify_email.txt', context)
    email = EmailMultiAlternatives(
        subject='Confirme seu e-mail | Mimos da Nick',
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    email.attach_alternative(html_content, 'text/html')
    email.send()


def verify_email_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        verification_token = EmailVerificationToken.objects.get(user=user, token=token, used=False)

        if verification_token.is_valid():
            profile = user.profile
            profile.email_verified = True
            profile.email_verified_at = timezone.now()
            profile.save()

            verification_token.used = True
            verification_token.save()

            login(request, user)
            request.session.pop('user_id', None)

            carrinho_sessao = request.session.get('carrinho', {})
            for produto_id, quantidade in carrinho_sessao.items():
                item, created = ItemCarrinho.objects.get_or_create(
                    usuario=user,
                    produto_id=produto_id,
                    defaults={'quantidade': quantidade}
                )
                if not created:
                    item.quantidade += quantidade
                    item.save()
            request.session['carrinho'] = {}

            next_url = request.session.pop('next_url', 'home')
            if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                next_url = 'home'

            messages.success(request, 'E-mail verificado com sucesso! Você já está logado 🎉')
            return redirect(next_url)
        else:
            messages.error(request, 'Este link de verificação expirou. Solicite um novo.')
            return redirect('resend_verification', user_id=user.id)

    except (User.DoesNotExist, EmailVerificationToken.DoesNotExist, ValueError):
        messages.error(request, 'Link de verificação inválido.')
        return redirect('login')


def verification_sent_view(request):
    user_id = request.session.get('user_id')
    return render(request, 'auth/verification_email.html', {'user_id': user_id})


def resend_verification_view(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
        EmailVerificationToken.objects.filter(user=user, used=False).update(used=True)
        send_verification_email(request, user)
        messages.success(request, 'Novo link de verificação enviado!')
    except User.DoesNotExist:
        messages.error(request, 'Usuário não encontrado.')
    return redirect('verification_email')


# =========================
# LOGOUT
# =========================
def logout_view(request):
    logout(request)
    messages.info(request, 'Logout realizado com sucesso!', extra_tags='logout')
    return redirect('home')


# =========================
# HOME
# =========================
def home_view(request):
    canecas = Produto.objects.filter(categoria__slug='canecas').order_by('-id').prefetch_related("categoria")[:8]
    agendas = Produto.objects.filter(categoria__slug='agendas').order_by('-id').prefetch_related("categoria")[:8]
    sublimacao = Produto.objects.filter(categoria__slug='sublimacao').order_by('-id').prefetch_related("categoria")[:8]
    return render(request, 'pages/home.html', {
        'canecas': canecas,
        'agendas': agendas,
        'sublimacao': sublimacao,
    })


# =========================
# OUTRAS VIEWS
# =========================
def cadernetas_view(request):
    return render(request, 'pages/cadernetas.html')

def contato_view(request):
    return render(request, 'pages/contato.html')

def carrinho_view(request):
    return render(request, 'pages/carrinho.html')


# =========================
# CÓDIGO POR E-MAIL
# =========================
def login_email_code_view(request):
    return render(request, 'auth/login_email_code.html')

def send_login_code_view(request):
    next_url = request.GET.get('next')
    if next_url:
        request.session['next_url'] = next_url

    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            messages.error(request, 'Informe um e-mail válido.', extra_tags='error')
            return redirect('login')

        code = login_code()
        LoginCode.create_code(email=email, code=code)

        contexto = {'code': code}
        mensagem_texto = render_to_string('emails/login_code_email.txt', contexto)
        mensagem_html = render_to_string('emails/login_code_email.html', contexto)

        email_msg = EmailMultiAlternatives(
            subject='Seu código de acesso | Mimos da Nick',
            body=mensagem_texto,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        email_msg.attach_alternative(mensagem_html, 'text/html')
        email_msg.send()

        messages.success(
            request,
            'Se existir uma conta com esse e-mail, você receberá um código de acesso.',
            extra_tags='login-code'
        )
        return redirect('login_code_confirm')
    return redirect('login')

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

        carrinho_sessao = request.session.get('carrinho', {})
        for produto_id, quantidade in carrinho_sessao.items():
            item, created = ItemCarrinho.objects.get_or_create(
                usuario=user,
                produto_id=produto_id,
                defaults={'quantidade': quantidade}
            )
            if not created:
                item.quantidade += quantidade
                item.save()
        request.session['carrinho'] = {}

        profile, _ = UserProfile.objects.get_or_create(user=user)
        if not profile.email_verified:
            profile.email_verified = True
            profile.email_verified_at = timezone.now()
            profile.save()

        if created:
            messages.success(request, 'Conta criada automaticamente com sucesso! Você já está logado 😊', extra_tags='login')
        else:
            messages.success(request, 'Login realizado com sucesso!', extra_tags='login')
        next_url = request.session.pop('next_url', 'home')
        return redirect(next_url)
    return render(request, 'auth/login_code.html')


# =========================
# RESET DE SENHA
# =========================
class PasswordResetCustomView(PasswordResetView):
    template_name = 'auth/password_reset.html'
    email_template_name = 'emails/password_reset_email.txt'
    html_email_template_name = 'emails/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')

    def form_valid(self, form):
        messages.success(self.request, 'Se existir uma conta com esse e-mail, você receberá instruções para redefinir sua senha.', extra_tags='success')
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
        messages.success(self.request, 'Senha redefinida com sucesso! Faça login com sua nova senha.', extra_tags='success')
        return super().form_valid(form)

class PasswordResetCompleteCustomView(PasswordResetCompleteView):
    template_name = 'auth/password_reset_complete.html'


# =========================
# BUSCA
# =========================
@require_GET
def search_products_view(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse({'results': []})
    produtos = Produto.objects.filter(nome__icontains=query)[:5]
    results = [
        {
            'id': produto.id,
            'nome': produto.nome,
            'slug': produto.slug,
            'imagem': produto.imagem.url if produto.imagem else '',
            'preco': str(produto.preco),
            'selo': produto.selo or '',
        }
        for produto in produtos
    ]
    return JsonResponse({'results': results})


# =========================
# PERFIL
# =========================
@login_required
def perfil_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        profile.nome_completo = request.POST.get("nome_completo", "")
        profile.cpf = request.POST.get("cpf", "")
        profile.telefone = request.POST.get("telefone", "")  # ✅ NOVO: salva telefone/WhatsApp
        profile.cep = request.POST.get("cep", "")
        profile.rua = request.POST.get("rua", "")
        profile.numero = request.POST.get("numero", "")
        profile.complemento = request.POST.get("complemento", "")
        profile.bairro = request.POST.get("bairro", "")
        profile.cidade = request.POST.get("cidade", "")
        profile.estado = request.POST.get("estado", "")
        profile.save()
        messages.success(request, "Perfil atualizado com sucesso!")
        return redirect("perfil")
    return render(request, "auth/perfil.html", {"profile": profile})


# =========================
# BUSCAR CEP
# =========================
def buscar_cep(request):
    cep = request.GET.get('cep', '').replace('.', '').replace('-', '')
    if len(cep) != 8:
        return JsonResponse({'erro': 'CEP inválido'})
    response = requests.get(f'https://viacep.com.br/ws/{cep}/json/', timeout=5)
    data = response.json()
    if data.get('erro'):
        return JsonResponse({'erro': 'CEP não encontrado'})
    return JsonResponse({
        'logradouro': data.get('logradouro', ''),
        'bairro': data.get('bairro', ''),
        'localidade': data.get('localidade', ''),
        'uf': data.get('uf', '')
    })


# =========================
# UTILITÁRIO
# =========================
def get_primeiro_nome(user):
    if user.first_name:
        return user.first_name.split()[0]
    return user.username