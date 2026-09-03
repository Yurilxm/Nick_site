from django.test import TestCase, Client
from django.test.utils import override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock
from decimal import Decimal
from produtos.models import Produto, Categoria
from carrinho.models import Carrinho, ItemCarrinho
from .models import Pedido, PedidoItem, Pagamento
from .services.pedido_service import criar_pedido
from .services.antifraude_service import validar_pedido_com_motivo
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
class PedidoTests(TestCase):
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
        self.carrinho = Carrinho.objects.create(usuario=self.user)
        self.item = ItemCarrinho.objects.create(carrinho=self.carrinho, produto=self.produto, quantidade=2, preco_unitario=29.90)

    def test_criar_pedido(self):
        endereco = {
            'nome_completo': 'Teste User',
            'cep': '22041-001',
            'rua': 'Rua Teste',
            'numero': '123',
            'bairro': 'Copacabana',
            'cidade': 'Rio de Janeiro',
            'estado': 'RJ',
        }
        pedido = criar_pedido(self.user, self.carrinho, {'valor': '15.00'}, endereco)
        self.assertEqual(pedido.total, Decimal('74.80'))
        self.assertEqual(pedido.itens.count(), 1)
        self.assertEqual(pedido.status, 'criado')

    def test_antifraude_cpf_invalido(self):
        endereco = {'nome_completo': 'Teste', 'cep': '22041001', 'rua': 'Rua', 'numero': '1', 'bairro': 'Bairro', 'cidade': 'Rio', 'estado': 'RJ'}
        pedido = criar_pedido(self.user, self.carrinho, {'valor': '0'}, endereco, cpf='11111111111')
        valido, motivo = validar_pedido_com_motivo(pedido)
        self.assertFalse(valido)
        self.assertIn('CPF inválido', motivo)

    def test_antifraude_valor_alto(self):
        endereco = {'nome_completo': 'Teste', 'cep': '22041001', 'rua': 'Rua', 'numero': '1', 'bairro': 'Bairro', 'cidade': 'Rio', 'estado': 'RJ'}
        # Cria pedido com total acima de 10000
        pedido = Pedido.objects.create(usuario=self.user, total=Decimal('15000.00'), status='criado')
        valido, motivo = validar_pedido_com_motivo(pedido)
        self.assertFalse(valido)
        self.assertIn('maior que R$ 10.000', motivo)

    @patch('pedidos.services.gateways.mercadopago_gateway.MercadoPagoGateway.criar_pix')
    def test_criar_pagamento_pix(self, mock_criar_pix):
        mock_criar_pix.return_value = {
            'id': '123456',
            'point_of_interaction': {
                'transaction_data': {
                    'qr_code': '000201...',
                    'qr_code_base64': 'base64string'
                }
            }
        }
        from .services.pagamento_service import criar_pagamento_pix
        pedido = Pedido.objects.create(usuario=self.user, total=59.80, status='aguardando_pagamento')
        pagamento = criar_pagamento_pix(pedido)
        self.assertEqual(pagamento.transaction_id, '123456')
        self.assertEqual(pagamento.metodo, 'pix')

    @patch('pedidos.services.gateways.mercadopago_gateway.MercadoPagoGateway.criar_cartao')
    def test_criar_pagamento_cartao_aprovado(self, mock_criar_cartao):
        mock_criar_cartao.return_value = {'id': '789', 'status': 'approved'}
        from .services.pagamento_service import criar_pagamento_cartao
        pedido = Pedido.objects.create(usuario=self.user, total=59.80, status='aguardando_pagamento')
        pagamento = criar_pagamento_cartao(pedido, token='abc', parcelas='1', bandeira='visa')
        self.assertEqual(pagamento.status, 'aprovado')
        self.assertEqual(pagamento.transaction_id, '789')

    @patch('pedidos.services.gateways.mercadopago_gateway.MercadoPagoGateway.criar_boleto')
    def test_criar_pagamento_boleto(self, mock_criar_boleto):
        mock_criar_boleto.return_value = {'id': '555', 'transaction_details': {'external_resource_url': 'http://boleto.com'}}
        from .services.pagamento_service import criar_pagamento_boleto
        pedido = Pedido.objects.create(usuario=self.user, total=59.80, status='aguardando_pagamento')
        pagamento = criar_pagamento_boleto(pedido)
        self.assertEqual(pagamento.transaction_id, '555')
        self.assertEqual(pagamento.boleto_url, 'http://boleto.com')

    @patch('pedidos.webhooks.mercadopago_webhook.sdk')
    @patch('pedidos.webhooks.mercadopago_webhook._validar_assinatura')
    def test_webhook_pagamento_aprovado(self, mock_validar, mock_sdk):
        mock_validar.return_value = True
        pedido = Pedido.objects.create(usuario=self.user, total=59.80, status='aguardando_pagamento')
        pagamento = Pagamento.objects.create(pedido=pedido, metodo='pix', transaction_id='123456', status='pendente')
        mock_sdk.payment.return_value.get.return_value = {'response': {'status': 'approved'}}
        url = reverse('pedidos:webhook_mercadopago')
        response = self.client.post(url, data=json.dumps({'data': {'id': '123456'}}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        pagamento.refresh_from_db()
        pedido.refresh_from_db()
        self.assertEqual(pagamento.status, 'aprovado')
        self.assertEqual(pedido.status, 'pago')

    @patch('pedidos.webhooks.mercadopago_webhook._validar_assinatura')
    def test_webhook_assinatura_invalida(self, mock_validar):
        mock_validar.return_value = False
        url = reverse('pedidos:webhook_mercadopago')
        response = self.client.post(url, data=json.dumps({'data': {'id': '123456'}}), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_acesso_nao_autenticado_redireciona(self):
        urls = [
            reverse('perfil'),
            reverse('carrinho:finalizar_compra'),
            reverse('pedidos:meus_pedidos'),
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)  # Redireciona para login
            self.assertIn('/login/', response.url)