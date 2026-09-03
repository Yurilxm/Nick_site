from django.test import TestCase, Client
from django.test.utils import override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock
from decimal import Decimal
from produtos.models import Produto, Categoria
from .models import Carrinho, ItemCarrinho
from .services import obter_carrinho
import json

STATIC_STORAGE_OVERRIDE = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

@override_settings(STORAGES=STATIC_STORAGE_OVERRIDE)
class CarrinhoTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='teste@example.com', email='teste@example.com', password='password123')
        self.user.profile.email_verified = True
        self.user.profile.save()
        self.categoria = Categoria.objects.create(nome='Canecas', slug='canecas')
        self.produto = Produto.objects.create(
            nome='Caneca Personalizada',
            slug='caneca-personalizada',
            preco=29.90,
            ativo=True,
        )
        self.produto.categoria.add(self.categoria)

    def test_adicionar_item_anonimo(self):
        response = self.client.post(reverse('carrinho:adicionar_ao_carrinho', args=[self.produto.id]), {
            'quantidade': 2,
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        carrinho = Carrinho.objects.get(usuario__isnull=True)
        item = carrinho.itens.first()
        self.assertEqual(item.quantidade, 2)

    def test_adicionar_item_logado(self):
        self.client.login(username='teste@example.com', password='password123')
        response = self.client.post(reverse('carrinho:adicionar_ao_carrinho', args=[self.produto.id]), {
            'quantidade': 1,
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        carrinho = Carrinho.objects.get(usuario=self.user)
        self.assertEqual(carrinho.itens.count(), 1)

    def test_migracao_carrinho_anonimo_para_logado(self):
        # Cria carrinho anônimo
        response = self.client.post(reverse('carrinho:adicionar_ao_carrinho', args=[self.produto.id]), {
            'quantidade': 1,
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        carrinho_anon = Carrinho.objects.get(usuario__isnull=True)
        # Faz login
        self.client.login(username='teste@example.com', password='password123')
        # O sinal deve migrar o carrinho
        carrinho_user = Carrinho.objects.filter(usuario=self.user).first()
        self.assertIsNotNone(carrinho_user)
        self.assertEqual(carrinho_user.itens.count(), 1)
        self.assertFalse(Carrinho.objects.filter(id=carrinho_anon.id).exists())

    def test_atualizar_quantidade(self):
        self.client.post(reverse('carrinho:adicionar_ao_carrinho', args=[self.produto.id]), {
            'quantidade': 1,
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        item = ItemCarrinho.objects.first()
        response = self.client.post(reverse('carrinho:aumentar_quantidade', args=[item.id]), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        item.refresh_from_db()
        self.assertEqual(item.quantidade, 2)

    def test_remover_item(self):
        self.client.post(reverse('carrinho:adicionar_ao_carrinho', args=[self.produto.id]), {
            'quantidade': 1,
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        item = ItemCarrinho.objects.first()
        response = self.client.post(reverse('carrinho:remover_do_carrinho', args=[item.id]), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(ItemCarrinho.objects.filter(id=item.id).exists())

    @patch('carrinho.views.calcular_frete_melhor_envio')
    def test_finalizar_compra_entrega(self, mock_frete):
        mock_frete.return_value = [{'id': '1', 'nome': 'PAC', 'transportadora': 'Correios', 'preco': '15.00', 'prazo': 5}]
        self.client.login(username='teste@example.com', password='password123')
        self.client.post(reverse('carrinho:adicionar_ao_carrinho', args=[self.produto.id]), {'quantidade': 1})
        response = self.client.get(reverse('carrinho:finalizar_compra'))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('carrinho:finalizar_compra'), {
            'tipo_entrega': 'entrega',
            'nome_completo': 'Teste User',
            'cep_entrega': '22041-001',
            'rua': 'Rua Teste',
            'numero': '123',
            'bairro': 'Copacabana',
            'cidade': 'Rio de Janeiro',
            'estado': 'RJ',
        }, follow=True)
        self.assertRedirects(response, reverse('pedidos:pagamento'))
        self.assertEqual(self.client.session['endereco']['rua'], 'Rua Teste')

    @patch('carrinho.views.calcular_frete_melhor_envio')
    def test_finalizar_compra_retirada(self, mock_frete):
        self.client.login(username='teste@example.com', password='password123')
        self.client.post(reverse('carrinho:adicionar_ao_carrinho', args=[self.produto.id]), {'quantidade': 1})
        response = self.client.post(reverse('carrinho:finalizar_compra'), {
            'tipo_entrega': 'retirada',
            'nome_completo_retirada': 'Teste User',
            'whatsapp_retirada': '(21) 99999-9999',
        }, follow=True)
        self.assertRedirects(response, reverse('pedidos:pagamento'))
        self.assertEqual(self.client.session['tipo_entrega'], 'retirada')
        self.assertNotIn('frete', self.client.session)

    def test_calcular_frete_cep_invalido(self):
        self.client.login(username='teste@example.com', password='password123')
        self.client.post(reverse('carrinho:adicionar_ao_carrinho', args=[self.produto.id]), {'quantidade': 1})
        response = self.client.post(reverse('carrinho:calcular_frete'), {
            'cep': '123',
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'erro')