from django.test import TestCase, Client
from django.test.utils import override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock
from decimal import Decimal
from produtos.models import Produto, Categoria
from pedidos.models import Pedido
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

    @patch('carrinho.views.calcular_frete_melhor_envio')
    def test_frete_do_carrinho_nao_some_na_confirmacao(self, mock_frete):
        mock_frete.return_value = [{'id': '1', 'nome': 'PAC', 'transportadora': 'Correios', 'preco': '12.58', 'prazo': 5}]
        self.client.login(username='teste@example.com', password='password123')
        self.client.post(reverse('carrinho:adicionar_ao_carrinho', args=[self.produto.id]), {'quantidade': 1})

        # Calcula frete no carrinho, sem preencher endereço ainda
        self.client.post(reverse('carrinho:calcular_frete'), {'cep': '22041001'})
        self.assertEqual(self.client.session['frete']['valor'], '12.58')

        # Vai direto para a confirmação (endereço ainda vazio)
        response = self.client.get(reverse('carrinho:finalizar_compra'))
        self.assertEqual(response.status_code, 200)
        # O frete não pode ter sido apagado
        self.assertIn('frete', self.client.session)
        self.assertEqual(self.client.session['frete']['valor'], '12.58')
        self.assertContains(response, '12,58')


@override_settings(STORAGES=STATIC_STORAGE_OVERRIDE)
class CarrinhoFluxoSincronizacaoTests(TestCase):
    """
    Testes dos cenários A-F descritos na auditoria do checkout:
    garantem que CEP, modalidade de entrega e frete permanecem
    consistentes conforme o cliente navega entre carrinho, confirmação
    e pagamento (avançando, voltando, trocando modalidade e CEP).
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='fluxo@example.com', email='fluxo@example.com', password='password123'
        )
        self.user.profile.email_verified = True
        self.user.profile.save()
        self.categoria = Categoria.objects.create(nome='Canecas', slug='canecas')
        self.produto = Produto.objects.create(
            nome='Caneca Fluxo',
            slug='caneca-fluxo',
            preco=Decimal('29.90'),
            ativo=True,
        )
        self.produto.categoria.add(self.categoria)
        self.client.login(username='fluxo@example.com', password='password123')
        self.client.post(
            reverse('carrinho:adicionar_ao_carrinho', args=[self.produto.id]),
            {'quantidade': 1},
        )

    def _preencher_endereco(self, cep):
        return {
            'tipo_entrega': 'entrega',
            'nome_completo': 'Cliente Teste',
            'cep_entrega': cep,
            'rua': 'Rua Teste',
            'numero': '123',
            'bairro': 'Copacabana',
            'cidade': 'Rio de Janeiro',
            'estado': 'RJ',
        }

    # =====================================================
    # Cenário B — troca de entrega para retirada
    # =====================================================
    @patch('carrinho.views.calcular_frete_melhor_envio')
    def test_cenario_b_frete_desaparece_ao_selecionar_retirada(self, mock_frete):
        mock_frete.return_value = [{
            'id': '1', 'nome': 'PAC', 'transportadora': 'Correios',
            'preco': '12.58', 'prazo': 5,
        }]
        # Frete calculado no carrinho
        self.client.post(reverse('carrinho:calcular_frete'), {'cep': '22041001'})
        self.assertEqual(self.client.session['frete']['valor'], '12.58')

        # Cliente muda para retirada na confirmação
        response = self.client.post(reverse('carrinho:finalizar_compra'), {
            'tipo_entrega': 'retirada',
            'nome_completo_retirada': 'Cliente Teste',
            'whatsapp_retirada': '(21) 99999-9999',
        }, follow=True)
        self.assertRedirects(response, reverse('pedidos:pagamento'))

        # Frete deve ter sido removido da sessão
        self.assertNotIn('frete', self.client.session)
        self.assertEqual(self.client.session['tipo_entrega'], 'retirada')

        # Pagamento deve refletir total sem frete
        response = self.client.get(reverse('pedidos:pagamento'))
        self.assertContains(response, '29,90')  # só o produto
        self.assertNotContains(response, '12,58')  # frete antigo não pode reaparecer

    @patch('pedidos.services.gateways.mercadopago_gateway.MercadoPagoGateway.criar_pix')
    @patch('carrinho.views.calcular_frete_melhor_envio')
    def test_cenario_b_pedido_criado_reflete_retirada(self, mock_frete, mock_criar_pix):
        mock_frete.return_value = [{
            'id': '1', 'nome': 'PAC', 'transportadora': 'Correios',
            'preco': '12.58', 'prazo': 5,
        }]
        mock_criar_pix.return_value = {
            'id': '999',
            'point_of_interaction': {
                'transaction_data': {'qr_code': 'x', 'qr_code_base64': 'y'}
            }
        }
        self.client.post(reverse('carrinho:calcular_frete'), {'cep': '22041001'})
        self.client.post(reverse('carrinho:finalizar_compra'), {
            'tipo_entrega': 'retirada',
            'nome_completo_retirada': 'Cliente Teste',
            'whatsapp_retirada': '(21) 99999-9999',
        })
        self.client.post(reverse('pedidos:pagamento'), {'metodo': 'pix'})

        pedido = Pedido.objects.latest('id')
        self.assertEqual(pedido.tipo_entrega, 'retirada')
        self.assertEqual(pedido.total, Decimal('29.90'))  # sem frete, mesmo tendo existido antes

    # =====================================================
    # Cenário C — volta de retirada para entrega
    # =====================================================
    @patch('carrinho.views.calcular_frete_melhor_envio')
    def test_cenario_c_frete_recalculado_ao_voltar_para_entrega(self, mock_frete):
        mock_frete.return_value = [{
            'id': '1', 'nome': 'PAC', 'transportadora': 'Correios',
            'preco': '18.20', 'prazo': 4,
        }]
        # Seleciona retirada primeiro
        self.client.post(reverse('carrinho:finalizar_compra'), {
            'tipo_entrega': 'retirada',
            'nome_completo_retirada': 'Cliente Teste',
            'whatsapp_retirada': '(21) 99999-9999',
        })
        self.assertNotIn('frete', self.client.session)

        # Volta para entrega e informa CEP
        self.client.post(reverse('carrinho:finalizar_compra'), self._preencher_endereco('22041-001'))

        # Volta a olhar a confirmação (GET) — frete deve ter sido recalculado
        response = self.client.get(reverse('carrinho:finalizar_compra'))
        self.assertIn('frete', self.client.session)
        self.assertEqual(self.client.session['frete']['valor'], '18.20')
        self.assertContains(response, '18,20')

    # =====================================================
    # Cenário D — CEP sobrevive a ida e volta de etapa
    # =====================================================
    @patch('carrinho.views.calcular_frete_melhor_envio')
    def test_cenario_d_cep_consistente_ao_voltar(self, mock_frete):
        mock_frete.return_value = [{
            'id': '1', 'nome': 'PAC', 'transportadora': 'Correios',
            'preco': '15.00', 'prazo': 5,
        }]
        self.client.post(reverse('carrinho:finalizar_compra'), self._preencher_endereco('22041-001'))
        self.assertEqual(self.client.session['endereco']['cep'], '22041-001')

        # Simula "voltar" (GET de novo na confirmação)
        response = self.client.get(reverse('carrinho:finalizar_compra'))
        self.assertEqual(self.client.session['endereco']['cep'], '22041-001')
        self.assertContains(response, '22041-001')

    # =====================================================
    # Cenário E — retirada sobrevive a ida ao pagamento e volta
    # =====================================================
    def test_cenario_e_modalidade_retirada_sobrevive_a_navegacao(self):
        self.client.post(reverse('carrinho:finalizar_compra'), {
            'tipo_entrega': 'retirada',
            'nome_completo_retirada': 'Cliente Teste',
            'whatsapp_retirada': '(21) 99999-9999',
        })
        # Avança para pagamento
        self.client.get(reverse('pedidos:pagamento'))
        # Volta para confirmação
        response = self.client.get(reverse('carrinho:finalizar_compra'))

        self.assertEqual(self.client.session['tipo_entrega'], 'retirada')
        self.assertIsNone(response.context['frete'])
        self.assertTrue(response.context['is_retirada'])
        self.assertNotContains(response, 'Frete (')

    # =====================================================
    # Cenário F — múltiplas trocas, estado final é o último válido
    # =====================================================
    @patch('carrinho.views.calcular_frete_melhor_envio')
    def test_cenario_f_ultima_escolha_prevalece_no_pagamento(self, mock_frete):
        mock_frete.side_effect = [
            [{'id': '1', 'nome': 'PAC', 'transportadora': 'Correios', 'preco': '10.00', 'prazo': 5}],
            [{'id': '2', 'nome': 'SEDEX', 'transportadora': 'Correios', 'preco': '22.30', 'prazo': 2}],
        ]
        # 1) entrega com CEP A — o cálculo só acontece no GET seguinte
        self.client.post(reverse('carrinho:finalizar_compra'), self._preencher_endereco('22041-001'))
        self.client.get(reverse('carrinho:finalizar_compra'))
        self.assertEqual(self.client.session['frete']['valor'], '10.00')

        # 2) troca para retirada
        self.client.post(reverse('carrinho:finalizar_compra'), {
            'tipo_entrega': 'retirada',
            'nome_completo_retirada': 'Cliente Teste',
            'whatsapp_retirada': '(21) 99999-9999',
        })
        self.assertNotIn('frete', self.client.session)

        # 3) volta para entrega com CEP B (diferente)
        self.client.post(reverse('carrinho:finalizar_compra'), self._preencher_endereco('20040-002'))
        response = self.client.get(reverse('carrinho:finalizar_compra'))  # força recálculo
        self.assertEqual(self.client.session['frete']['valor'], '22.30')

        # Pagamento deve refletir só o último estado (SEDEX 22,30, entrega)
        response = self.client.get(reverse('pedidos:pagamento'))
        self.assertFalse(response.context['is_retirada'])
        self.assertContains(response, '22,30')
        self.assertNotContains(response, '10,00')