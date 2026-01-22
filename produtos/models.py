from django.db import models
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

    class Meta:
        ordering = ['-criado_em']

    def __str__(self):
        return self.nome
    
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
