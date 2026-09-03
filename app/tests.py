from django.test import TestCase, Client
from django.test.utils import override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from unittest.mock import patch
from .models import UserProfile, EmailVerificationToken, LoginCode
from .forms import RegisterForm, LoginForm
from django.utils import timezone
from datetime import timedelta

STATIC_STORAGE_OVERRIDE = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

@override_settings(STORAGES=STATIC_STORAGE_OVERRIDE)
class AuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('login')
        self.home_url = reverse('home')

    def test_registro_usuario_valido(self):
        response = self.client.post(self.register_url, {
            'register_submit': '1',
            'nome': 'Teste User',
            'email': 'teste@example.com',
            'password1': 'Senha123!',
            'password2': 'Senha123!',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(email='teste@example.com').exists())
        user = User.objects.get(email='teste@example.com')
        self.assertFalse(user.profile.email_verified)
        self.assertRedirects(response, reverse('verification_email'))

    def test_registro_email_duplicado(self):
        User.objects.create_user(username='teste@example.com', email='teste@example.com', password='password123')
        response = self.client.post(self.register_url, {
            'register_submit': '1',
            'nome': 'Outro User',
            'email': 'teste@example.com',
            'password1': 'Senha123!',
            'password2': 'Senha123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email='teste@example.com').count() > 1)

    def test_login_sucesso(self):
        user = User.objects.create_user(username='teste@example.com', email='teste@example.com', password='password123')
        user.profile.email_verified = True
        user.profile.save()
        response = self.client.post(reverse('login'), {
            'login_submit': '1',
            'username': 'teste@example.com',
            'password': 'password123',
        }, follow=True)
        self.assertRedirects(response, self.home_url)
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def test_login_senha_incorreta(self):
        User.objects.create_user(username='teste@example.com', email='teste@example.com', password='password123')
        response = self.client.post(reverse('login'), {
            'login_submit': '1',
            'username': 'teste@example.com',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_login_usuario_nao_verificado(self):
        user = User.objects.create_user(username='teste@example.com', email='teste@example.com', password='password123')
        response = self.client.post(reverse('login'), {
            'login_submit': '1',
            'username': 'teste@example.com',
            'password': 'password123',
        }, follow=True)
        self.assertRedirects(response, reverse('verification_email'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_verificacao_email(self):
        user = User.objects.create_user(username='teste@example.com', email='teste@example.com', password='password123')
        token = EmailVerificationToken.create_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        url = reverse('verify_email', kwargs={'uidb64': uid, 'token': token.token})
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, self.home_url)
        user.refresh_from_db()
        self.assertTrue(user.profile.email_verified)

    def test_login_via_codigo(self):
        email = 'codigo@example.com'
        User.objects.create_user(username=email, email=email, password='password123')
        code = '123456'
        LoginCode.create_code(email=email, code=code)
        response = self.client.post(reverse('login_code_confirm'), {'code': code}, follow=True)
        self.assertRedirects(response, self.home_url)
        user = User.objects.get(email=email)
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)
        self.assertTrue(user.profile.email_verified)

    def test_login_via_codigo_invalido(self):
        response = self.client.post(reverse('login_code_confirm'), {'code': '000000'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_logout(self):
        user = User.objects.create_user(username='teste@example.com', email='teste@example.com', password='password123')
        user.profile.email_verified = True
        user.profile.save()
        self.client.login(username='teste@example.com', password='password123')
        response = self.client.post(reverse('logout'), follow=True)
        self.assertRedirects(response, self.home_url)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_perfil_atualizacao(self):
        user = User.objects.create_user(username='teste@example.com', email='teste@example.com', password='password123')
        user.profile.email_verified = True
        user.profile.save()
        self.client.login(username='teste@example.com', password='password123')
        response = self.client.post(reverse('perfil'), {
            'nome_completo': 'Novo Nome',
            'cpf': '123.456.789-00',
            'telefone': '(21) 99999-9999',
            'cep': '22041-001',
            'rua': 'Rua Teste',
            'numero': '123',
            'bairro': 'Copacabana',
            'cidade': 'Rio de Janeiro',
            'estado': 'RJ',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertEqual(user.profile.nome_completo, 'Novo Nome')
        self.assertEqual(user.profile.cpf, '12345678900')

    def test_reenviar_verificacao(self):
        user = User.objects.create_user(username='teste@example.com', email='teste@example.com', password='password123')
        # Precisamos que a sessão tenha user_id para a página de verificação
        self.client.session['user_id'] = user.id
        self.client.session.save()
        response = self.client.post(reverse('resend_verification', args=[user.id]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('verification_email'))

@override_settings(STORAGES=STATIC_STORAGE_OVERRIDE)
class FormTests(TestCase):
    def test_register_form_nome_com_numero(self):
        form = RegisterForm(data={
            'nome': 'Teste 123',
            'email': 'teste@example.com',
            'password1': 'Senha123!',
            'password2': 'Senha123!',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('nome', form.errors)

    def test_register_form_senha_curta(self):
        form = RegisterForm(data={
            'nome': 'Teste',
            'email': 'teste@example.com',
            'password1': '123',
            'password2': '123',
        })
        self.assertFalse(form.is_valid())

    def test_login_form_credenciais_erradas(self):
        User.objects.create_user(username='teste@example.com', email='teste@example.com', password='password123')
        form = LoginForm(data={'username': 'teste@example.com', 'password': 'wrongpassword'})
        self.assertFalse(form.is_valid())

@override_settings(STORAGES=STATIC_STORAGE_OVERRIDE)
class ModelTests(TestCase):
    def test_userprofile_cpf_formatado(self):
        user = User.objects.create_user(username='cpf@example.com', email='cpf@example.com', password='password123')
        profile = user.profile
        profile.cpf = '12345678900'
        profile.save()
        self.assertEqual(profile.get_cpf_formatado(), '123.456.789-00')

    def test_userprofile_telefone_limpo(self):
        user = User.objects.create_user(username='tel@example.com', email='tel@example.com', password='password123')
        profile = user.profile
        profile.telefone = '(21) 99999-9999'
        profile.save()
        self.assertEqual(profile.telefone, '21999999999')