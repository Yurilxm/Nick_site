from django.test import TestCase, Client
from django.test.utils import override_settings
from django.urls import reverse
from django.core.exceptions import ValidationError
from decimal import Decimal
from .models import Categoria, Produto

STATIC_STORAGE_OVERRIDE = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

@override_settings(STORAGES=STATIC_STORAGE_OVERRIDE)
class ProdutoTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.categoria = Categoria.objects.create(nome='Canecas', slug='canecas')
        self.produto_ativo = Produto.objects.create(
            nome='Caneca Personalizada',
            slug='caneca-personalizada',
            preco=Decimal('29.90'),
            ativo=True,
        )
        self.produto_ativo.categoria.add(self.categoria)
        self.produto_inativo = Produto.objects.create(
            nome='Caneca Inativa',
            slug='caneca-inativa',
            preco=Decimal('19.90'),
            ativo=False,
        )

    def test_listagem_produtos_ativos(self):
        response = self.client.get(reverse('lista_produtos'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Caneca Personalizada')
        self.assertNotContains(response, 'Caneca Inativa')

    def test_detalhe_produto(self):
        url = reverse('detalhe_produto', kwargs={'produto_id': self.produto_ativo.id, 'slug': self.produto_ativo.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Caneca Personalizada')

    def test_detalhe_produto_inativo_404(self):
        url = reverse('detalhe_produto', kwargs={'produto_id': self.produto_inativo.id, 'slug': self.produto_inativo.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_produtos_por_categoria(self):
        url = reverse('produtos_por_categoria', kwargs={'slug': self.categoria.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Caneca Personalizada')

    def test_preco_pix(self):
        self.assertEqual(self.produto_ativo.preco_pix, Decimal('28.40'))

    def test_preco_parcela_2x(self):
        self.assertEqual(self.produto_ativo.preco_parcela_2x, Decimal('14.95'))

    def test_slug_automatico(self):
        produto = Produto.objects.create(nome='Produto Teste Slug', preco=Decimal('10.00'), ativo=True)
        self.assertEqual(produto.slug, 'produto-teste-slug')

    def test_validacao_extensao_imagem(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        from django.core.exceptions import ValidationError
        produto = Produto(nome='Produto Imagem', preco=Decimal('10.00'))
        arquivo = SimpleUploadedFile("teste.gif", b"GIF89a", content_type="image/gif")
        produto.imagem = arquivo
        with self.assertRaises(ValidationError):
            produto.full_clean()