from django.db import models
from django.utils.text import slugify
from django.urls import reverse


class Produto(models.Model):
    nome = models.CharField(max_length=150)

    selo = models.CharField(
        max_length=50,
        blank=True,
        help_text="Ex: Novo, Promoção, Lançamento, Últimas unidades"
    )

    slug = models.SlugField(
        unique=True, blank=True, max_length=160, editable=False, db_index=True
    )

    descricao = models.TextField(blank=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)

    peso = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        default=0.3,
        help_text="Peso em kg (ex: 0.300)"
    )

    altura = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=10,
        help_text="Altura em cm"
    )

    largura = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=10,
        help_text="Largura em cm"
    )

    comprimento = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=10,
        help_text="Comprimento em cm"
    )

    imagem = models.ImageField(upload_to="produtos/", blank=True)

    permite_personalizacao = models.BooleanField(default=False)

    ativo = models.BooleanField(default=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    categoria = models.ForeignKey(
        "Categoria",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="produtos",
    )

    class Meta:
        ordering = ["-criado_em"]

    def __str__(self):
        return self.nome

    def imagens_hover(self):
        return self.imagens.filter(tipo="hover")

    def tem_hover(self):
        return self.imagens.filter(tipo="hover").exists()

    def imagens_detalhe(self):
        return self.imagens.filter(tipo="detalhe")

    def save(self, *args, **kwargs):
        if not self.slug:
            slug_base = slugify(self.nome)
            slug = slug_base
            contador = 1

            while Produto.objects.filter(slug=slug).exists():
                slug = f"{slug_base}-{contador}"
                contador += 1
            self.slug = slug

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("detalhe_produto", kwargs={"id": self.id, "slug": self.slug})
    

class GrupoOpcao(models.Model):

    TIPO_CHOICES = (
        ("radio", "Radio"),
        ("select", "Select"),
        ("checkbox", "Checkbox"),
        ("texto", "Campo de Texto"),
    )

    produto = models.ForeignKey(
        Produto,
        on_delete=models.CASCADE,
        related_name="grupos_opcoes"
    )

    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    obrigatorio = models.BooleanField(default=True)
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["ordem"]

    def __str__(self):
        return f"{self.nome} - {self.produto.nome}"


class Opcao(models.Model):
    grupo = models.ForeignKey(
        GrupoOpcao,
        on_delete=models.CASCADE,
        related_name="opcoes"
    )

    nome = models.CharField(max_length=100)
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["ordem"]

    def __str__(self):
        return f"{self.nome} ({self.grupo.nome})"


class Categoria(models.Model):
    nome = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Categorias"
        ordering = ["ordem"]

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)


class ProdutoImagem(models.Model):

    TIPO_CHOICES = (
        ("hover", "Imagem de hover"),
        ("detalhe", "Imagem de detalhe"),
    )

    produto = models.ForeignKey(
        Produto, on_delete=models.CASCADE, related_name="imagens"
    )

    imagem = models.ImageField(upload_to="produtos/galeria/")
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default="detalhe")
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["ordem"]
        verbose_name = "Imagem do Produto"
        verbose_name_plural = "Imagens do Produto"
        constraints = [
            models.UniqueConstraint(
                fields=["produto"],
                condition=models.Q(tipo="hover"),
                name="unique_hover_image_por_produto",
            )
        ]

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.produto.nome}"



class ConfiguracaoSobre(models.Model):
    foto_equipe = models.ImageField(
        upload_to="sobre/",
        blank=True,
        null=True,
        help_text="Foto da equipe/loja exibida na seção 'Nossa história'"
    )

    class Meta:
        verbose_name = "Configuração da Página Sobre"
        verbose_name_plural = "Configuração da Página Sobre"

    def __str__(self):
        return "Configuração da Página Sobre"

    def save(self, *args, **kwargs):
        # Garante que só existe um registro
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj



class Avaliacao(models.Model):
    nome = models.CharField(max_length=100)
    comentario = models.TextField()
    estrelas = models.PositiveIntegerField(default=5)

    foto = models.ImageField(upload_to="avaliacoes/", blank=True, null=True)

    aprovado = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "Avaliação"
        verbose_name_plural = "Avaliações"

    def __str__(self):
        return f"{self.nome} ({self.estrelas}⭐)"


class ImagemSobre(models.Model):
    imagem = models.ImageField(upload_to="sobre/")
    ordem = models.PositiveIntegerField(default=0)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "Imagem da Página Sobre"
        verbose_name_plural = "Imagens da Página Sobre"

    def __str__(self):
        return f"Imagem Sobre #{self.id}"