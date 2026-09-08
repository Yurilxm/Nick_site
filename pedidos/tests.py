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
            preco=Decimal('29.90'),
            ativo=True,
        )
        self.produto.categoria.add(self.categoria)
        self.carrinho = Carrinho.objects.create(usuario=self.user)
        self.item = ItemCarrinho.objects.create(carrinho=self.carrinho, produto=self.produto, quantidade=2, preco_unitario=Decimal('29.90'))

    def criar_pedido_retirada(self):
        endereco = {
            'nome_completo': 'Teste User',
            'cep': '',
            'rua': '',
            'numero': '',
            'bairro': '',
            'cidade': '',
            'estado': '',
        }
        pedido = criar_pedido(
            usuario=self.user,
            carrinho=self.carrinho,
            frete={},
            endereco=endereco,
            cpf=None,
        )
        pedido.tipo_entrega = 'retirada'
        pedido.whatsapp_retirada = '21999999999'
        pedido.status = 'aguardando_pagamento'
        pedido.save()
        return pedido

    # =====================================================
    # Retirada
    # =====================================================
    def test_retirada_total_sem_frete(self):
        pedido = self.criar_pedido_retirada()
        self.assertEqual(pedido.total, Decimal('59.80'))  # 2 x 29.90
        self.assertEqual(pedido.valor_frete, Decimal('0.00'))
        self.assertTrue(pedido.is_retirada)

    @patch('pedidos.views.calcular_frete_melhor_envio')
    def test_view_pagamento_retirada_sem_frete(self, mock_frete):
        self.client.login(username='teste@example.com', password='password123')
        # Limpa o carrinho para ter apenas 1 item
        self.carrinho.itens.all().delete()
        # Simula sessão de retirada
        session = self.client.session
        session['tipo_entrega'] = 'retirada'
        session['whatsapp_retirada'] = '21999999999'
        session.save()
        # Adiciona 1 item ao carrinho
        self.client.post(reverse('carrinho:adicionar_ao_carrinho', args=[self.produto.id]), {'quantidade': 1})
        response = self.client.get(reverse('pedidos:pagamento'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Frete')
        self.assertContains(response, 'Retirada na loja')
        # Verifica que o total exibido é apenas o produto
        self.assertContains(response, '29,90')

    # =====================================================
    # Pagamento PIX
    # =====================================================
    @patch('pedidos.services.gateways.mercadopago_gateway.MercadoPagoGateway.criar_pix')
    def test_view_pagamento_pix_retirada(self, mock_criar_pix):
        mock_criar_pix.return_value = {
            'id': '123456',
            'point_of_interaction': {
                'transaction_data': {
                    'qr_code': '000201...',
                    'qr_code_base64': 'base64string'
                }
            }
        }
        self.client.login(username='teste@example.com', password='password123')
        # Limpa o carrinho para ter apenas 1 item
        self.carrinho.itens.all().delete()
        # Configura sessão para retirada
        session = self.client.session
        session['tipo_entrega'] = 'retirada'
        session['whatsapp_retirada'] = '21999999999'
        session['endereco'] = {'nome_completo': 'Teste User', 'cep': '', 'rua': '', 'numero': '', 'bairro': '', 'cidade': '', 'estado': ''}
        session.save()
        # Adiciona 1 item
        self.client.post(reverse('carrinho:adicionar_ao_carrinho', args=[self.produto.id]), {'quantidade': 1})
        # Faz POST para pagamento PIX
        response = self.client.post(reverse('pedidos:pagamento'), {'metodo': 'pix'}, follow=True)
        self.assertEqual(response.status_code, 200)
        # Verifica que um pedido foi criado
        pedido = Pedido.objects.latest('id')
        self.assertEqual(pedido.tipo_entrega, 'retirada')
        self.assertEqual(pedido.whatsapp_retirada, '21999999999')
        self.assertEqual(pedido.total, Decimal('29.90'))  # sem frete
        # Verifica que a página PIX foi renderizada
        self.assertTemplateUsed(response, 'pedidos/pagamentos/pix.html')

    # =====================================================
    # Webhook
    # =====================================================
    @patch('pedidos.webhooks.mercadopago_webhook.sdk')
    @patch('pedidos.webhooks.mercadopago_webhook._validar_assinatura')
    def test_webhook_aprovado_atualiza_pedido(self, mock_validar, mock_sdk):
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

    @patch('pedidos.webhooks.mercadopago_webhook.sdk')
    @patch('pedidos.webhooks.mercadopago_webhook._validar_assinatura')
    def test_webhook_status_nao_aprovado_nao_muda(self, mock_validar, mock_sdk):
        mock_validar.return_value = True
        pedido = Pedido.objects.create(usuario=self.user, total=59.80, status='aguardando_pagamento')
        pagamento = Pagamento.objects.create(pedido=pedido, metodo='pix', transaction_id='123456', status='pendente')
        mock_sdk.payment.return_value.get.return_value = {'response': {'status': 'pending'}}
        url = reverse('pedidos:webhook_mercadopago')
        response = self.client.post(url, data=json.dumps({'data': {'id': '123456'}}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        pagamento.refresh_from_db()
        pedido.refresh_from_db()
        self.assertEqual(pagamento.status, 'pendente')
        self.assertEqual(pedido.status, 'aguardando_pagamento')

    def test_webhook_assinatura_invalida(self):
        url = reverse('pedidos:webhook_mercadopago')
        response = self.client.post(url, data=json.dumps({'data': {'id': '123456'}}), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    # =====================================================
    # PDF
    # =====================================================
    def test_pdf_retirada_gera_pdf(self):
        pedido = self.criar_pedido_retirada()
        url = reverse('pedidos:pedido_pdf', args=[pedido.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    # =====================================================
    # Admin Ficha de Produção
    # =====================================================
    def test_admin_ficha_producao_retirada(self):
        from pedidos.admin import PedidoAdmin
        pedido = self.criar_pedido_retirada()
        admin = PedidoAdmin(Pedido, None)
        html = admin.ficha_producao(pedido)
        self.assertIn('Retirada na loja', html)
        self.assertIn('21999999999', html)
        self.assertNotIn('CEP', html)  # não deve exibir CEP para retirada


@override_settings(STORAGES=STATIC_STORAGE_OVERRIDE)
class PagamentoSincronizacaoTests(TestCase):
    """
    Cenários A-F focados na view de pagamento: garante que o total exibido
    e o total salvo no Pedido sempre refletem o último estado válido de
    frete/modalidade da sessão, mesmo após idas e vindas entre etapas.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='pgto@example.com', email='pgto@example.com', password='password123'
        )
        self.user.profile.email_verified = True
        self.user.profile.save()
        self.categoria = Categoria.objects.create(nome='Canecas', slug='canecas')
        self.produto = Produto.objects.create(
            nome='Caneca Pagamento', slug='caneca-pagamento',
            preco=Decimal('29.90'), ativo=True,
        )
        self.produto.categoria.add(self.categoria)
        self.client.login(username='pgto@example.com', password='password123')
        self.client.post(
            reverse('carrinho:adicionar_ao_carrinho', args=[self.produto.id]),
            {'quantidade': 1},
        )

    @patch('pedidos.views.calcular_frete_melhor_envio')
    def test_pagamento_get_recalcula_frete_ausente_com_cep_valido(self, mock_frete):
        mock_frete.return_value = [{
            'id': '1', 'nome': 'PAC', 'transportadora': 'Correios',
            'preco': '9.90', 'prazo': 6,
        }]
        session = self.client.session
        session['endereco'] = {
            'nome_completo': 'Cliente Teste', 'cep': '22041-001', 'rua': 'Rua Teste',
            'numero': '10', 'bairro': 'Copacabana', 'cidade': 'Rio de Janeiro', 'estado': 'RJ',
        }
        session['tipo_entrega'] = 'entrega'
        session.pop('frete', None)
        session.save()

        response = self.client.get(reverse('pedidos:pagamento'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('frete', self.client.session)
        self.assertEqual(self.client.session['frete']['valor'], '9.90')
        self.assertContains(response, '9,90')

    def test_pagamento_get_nao_calcula_frete_sem_cep(self):
        session = self.client.session
        session['endereco'] = {'nome_completo': 'Cliente Teste', 'cep': ''}
        session['tipo_entrega'] = 'entrega'
        session.save()

        response = self.client.get(reverse('pedidos:pagamento'))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('frete', self.client.session)