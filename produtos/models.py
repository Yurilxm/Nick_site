from django.db import models
from django.forms import ValidationError
from django.utils.text import slugify



class Produto(models.Model):
    nome = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, blank=True, max_length=160, editable=False, db_index=True)

    descricao = models.TextField(blank=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)

    imagem = models.ImageField(upload_to='produtos/', blank=True)

    ativo = models.BooleanField(default=True)
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    categoria = models.ForeignKey('Categoria', on_delete=models.SET_NULL, null=True, blank=True, related_name='produtos')

    class Meta:
        ordering = ['-criado_em']

    def __str__(self):
        return self.nome
    
    def imagens_hover(self):
        return self.imagens.filter(tipo='hover')

    def tem_hover(self):
        return self.imagens.filter(tipo='hover').exists()

    def imagens_detalhe(self):
        return self.imagens.filter(tipo='detalhe')
    
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


class Categoria(models.Model):
    nome = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Categorias"

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.nome.lower().replace(" ", "-")
        super().save(*args, **kwargs)


class ProdutoImagem(models.Model):

    TIPO_CHOICES = (
        ('hover', 'Imagem de hover'),
        ('detalhe', 'Imagem de detalhe'),
    )

    produto = models.ForeignKey(
        Produto,
        on_delete=models.CASCADE,
        related_name='imagens'
    )

    imagem = models.ImageField(upload_to='produtos/galeria/')
    tipo = models.CharField(
        max_length=10,
        choices=TIPO_CHOICES,
        default='detalhe'
    )
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordem']
        verbose_name = 'Imagem do Produto'
        verbose_name_plural = 'Imagens do Produto'

    def clean(self):
        if self.tipo == 'hover':
            existe_hover = ProdutoImagem.objects.filter(
                produto=self.produto,
                tipo='hover'
            ).exclude(pk=self.pk).exists()

            if existe_hover:
                raise ValidationError(
                    'Este produto já possui uma imagem de hover.'
                )

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.produto.nome}"