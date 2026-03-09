from django.db import models
from django.conf import settings


class Pedido(models.Model):

    STATUS_CHOICES = [
        ("aguardando_pagamento", "Aguardando pagamento"),
        ("pago", "Pago"),
        ("em_producao", "Em produção"),
        ("enviado", "Enviado"),
        ("entregue", "Entregue"),
        ("cancelado", "Cancelado"),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="pedidos"
    )

    data_criacao = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="aguardando_pagamento"
    )

    total_produtos = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    valor_frete = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    total_geral = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    cep_entrega = models.CharField(
        max_length=9,
        blank=True,
        null=True
    )

    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario}"


class PedidoItem(models.Model):

    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name="itens"
    )

    produto = models.ForeignKey(
        "produtos.Produto",
        on_delete=models.PROTECT
    )

    preco_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    quantidade = models.PositiveIntegerField()

    opcoes = models.JSONField(
        blank=True,
        null=True
    )

    def subtotal(self):
        return self.preco_unitario * self.quantidade

    def __str__(self):
        return f"{self.produto} x{self.quantidade}"