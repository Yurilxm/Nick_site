import os
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "1")

import unittest
from decimal import Decimal
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import Client
from django.test.utils import override_settings
from django.contrib.auth.models import User
from produtos.models import Produto, Categoria

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

STATIC_STORAGE_OVERRIDE = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}


@unittest.skipUnless(
    PLAYWRIGHT_AVAILABLE,
    "Playwright não instalado. Rode: pip install playwright && playwright install chromium"
)
@override_settings(STORAGES=STATIC_STORAGE_OVERRIDE)
class CheckoutToggleE2ETests(StaticLiveServerTestCase):
    """
    Teste de browser real (não usa django.test.Client) para o único tipo
    de bug que testes de backend não conseguem pegar: JS que não reage
    a um clique. Cobre especificamente o toggle "Receber em casa" /
    "Retirar na loja" na etapa de confirmação.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create_user(
            username='e2e@example.com', email='e2e@example.com', password='password123'
        )
        self.user.profile.email_verified = True
        self.user.profile.save()
        categoria = Categoria.objects.create(nome='Canecas', slug='canecas')
        self.produto = Produto.objects.create(
            nome='Caneca E2E', slug='caneca-e2e', preco=Decimal('29.90'), ativo=True,
        )
        self.produto.categoria.add(categoria)

        # Autentica e monta carrinho via backend (Client normal do Django) —
        # evita depender dos seletores exatos do formulário de login/HTML,
        # e deixa o Playwright focado só em testar a interação do toggle.
        django_client = Client()
        django_client.login(username='e2e@example.com', password='password123')
        django_client.post(f'/carrinho/adicionar/{self.produto.id}/', {'quantidade': 1})

        session_cookie = django_client.cookies['sessionid']

        self.context = self.browser.new_context()
        self.context.add_cookies([{
            'name': 'sessionid',
            'value': session_cookie.value,
            'url': self.live_server_url,
        }])
        self.page = self.context.new_page()

    def tearDown(self):
        self.context.close()

    def test_toggle_para_retirada_esconde_frete_sem_reload(self):
        self.page.goto(f"{self.live_server_url}/carrinho/finalizar/")

        # Garante que começou no modo "entrega" (padrão)
        self.page.wait_for_selector('#radio-entrega', state='attached')

        # Clica em "Retirar na loja"
        self.page.click('#label-retirada')

        # O bloco de retirada deve aparecer e o de entrega sumir,
        # SEM reload de página — se o listener não existir, isso nunca
        # vira 'visible'/'hidden' e o teste falha por timeout.
        self.page.wait_for_selector('#bloco-retirada', state='visible', timeout=3000)
        self.page.wait_for_selector('#bloco-entrega', state='hidden', timeout=3000)

        # Linha de frete não pode continuar visível
        frete_pendente = self.page.query_selector('#linha-frete-pendente')
        if frete_pendente:
            self.assertFalse(frete_pendente.is_visible())

        frete_atual = self.page.query_selector('#linha-frete-atual')
        if frete_atual:
            self.assertFalse(frete_atual.is_visible())

    def test_toggle_para_retirada_e_volta_para_entrega(self):
        self.page.goto(f"{self.live_server_url}/carrinho/finalizar/")
        self.page.wait_for_selector('#radio-entrega', state='attached')

        self.page.click('#label-retirada')
        self.page.wait_for_selector('#bloco-retirada', state='visible', timeout=3000)

        self.page.click('#label-entrega')
        self.page.wait_for_selector('#bloco-entrega', state='visible', timeout=3000)
        self.page.wait_for_selector('#bloco-retirada', state='hidden', timeout=3000)

        # Confirma que o rádio de fato reflete o estado visual
        self.assertTrue(self.page.is_checked('#radio-entrega'))
        self.assertFalse(self.page.is_checked('#radio-retirada'))
