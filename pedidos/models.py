from django.db import models
from django.conf import settings
import uuid

User = settings.AUTH_USER_MODEL


class Pedido(models.Model):

    STATUS_CHOICES = [
        ("criado", "Criado"),
        ("aguardando_pagamento", "Aguardando pagamento"),
        ("pago", "Pago"),
        ("cancelado", "Cancelado"),
        ("expirado", "Expirado"),
        ("enviado", "Enviado"),
        ("entregue", "Entregue"),
    ]

    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    cep_entrega = models.CharField(
        max_length=9
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="criado"
    )

    reservado_ate = models.DateTimeField(
        null=True,
        blank=True
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Pedido {self.id}"


class PedidoItem(models.Model):

    pedido = models.ForeignKey(
        Pedido,
        related_name="itens",
        on_delete=models.CASCADE
    )

    produto = models.ForeignKey(
        "produtos.Produto",
        on_delete=models.PROTECT
    )

    quantidade = models.PositiveIntegerField()

    preco_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def subtotal(self):
        return self.preco_unitario * self.quantidade


class Pagamento(models.Model):

    METODO_CHOICES = [
        ("pix", "Pix"),
        ("cartao", "Cartão"),
        ("boleto", "Boleto"),
    ]

    STATUS_CHOICES = [
        ("pendente", "Pendente"),
        ("aprovado", "Aprovado"),
        ("recusado", "Recusado"),
    ]

    pedido = models.ForeignKey(
        Pedido,
        related_name="pagamentos",
        on_delete=models.CASCADE
    )

    metodo = models.CharField(
        max_length=20,
        choices=METODO_CHOICES
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pendente"
    )

    transaction_id = models.CharField(
        max_length=200,
        unique=True
    )

    idempotency_key = models.UUIDField(
        default=uuid.uuid4,
        unique=True
    )

    qr_code = models.TextField(
        blank=True
    )

    qr_code_base64 = models.TextField(
        blank=True
    )

    boleto_url = models.URLField(
        blank=True
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    pix_expira_em = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Pagamento {self.id}"