from django.conf import settings
from django.db import models
from produtos.models import Produto


class Carrinho(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='carrinhos'
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        if self.usuario:
            return f"Carrinho de {self.usuario}"
        return f"Carrinho anônimo ({self.id})"


class ItemCarrinho(models.Model):
    carrinho = models.ForeignKey(
        Carrinho,
        on_delete=models.CASCADE,
        related_name='itens'
    )
    produto = models.ForeignKey(
        Produto,
        on_delete=models.CASCADE
    )
    quantidade = models.PositiveIntegerField(default=1)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('carrinho', 'produto')

    def subtotal(self):
        return self.quantidade * self.preco_unitario

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome}"
