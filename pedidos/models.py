from django.db import models
from django.conf import settings
import uuid

User = settings.AUTH_USER_MODEL


class Pedido(models.Model):

    STATUS_CHOICES = [
        ("criado", "Criado"),
        ("aguardando_pagamento", "Aguardando pagamento"),
        ("pago", "Pago"),
        ("em_producao", "Em produção"),
        ("cancelado", "Cancelado"),
        ("expirado", "Expirado"),
        ("enviado", "Enviado"),
        ("entregue", "Entregue"),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    total = models.DecimalField(max_digits=10, decimal_places=2)

    cep_entrega = models.CharField(max_length=9, blank=True)
    rua = models.CharField(max_length=200, blank=True)
    numero = models.CharField(max_length=20, blank=True)
    bairro = models.CharField(max_length=100, blank=True)
    cidade = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=2, blank=True)
    complemento = models.CharField(max_length=200, blank=True)
    cpf = models.CharField(max_length=14, blank=True, null=True)
    nome_cliente = models.CharField(max_length=200, blank=True, verbose_name="Nome completo")

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="criado"
    )

    criado_em = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        from pedidos.services.email_service import (
            enviar_email_pedido_confirmado,
            enviar_email_pedido_enviado
        )

        is_update = self.pk is not None

        if is_update:
            old = Pedido.objects.filter(pk=self.pk).first()

            if old and old.status != self.status:

                # Pedido pago → envia email de confirmação
                if self.status == "pago":
                    if self.usuario and self.usuario.email:
                        enviar_email_pedido_confirmado(self)

                # Pedido enviado → envia email de envio
                if self.status == "enviado":
                    if self.usuario and self.usuario.email:
                        enviar_email_pedido_enviado(self)

        super().save(*args, **kwargs)

    @property
    def total_produtos(self):
        return sum(item.subtotal for item in self.itens.all())

    @property
    def valor_frete(self):
        return self.total - self.total_produtos

    @property
    def total_geral(self):
        return self.total

    def __str__(self):
        return f"Pedido {self.id} - {self.status}"


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

    opcoes = models.JSONField(
        blank=True,
        null=True
    )

    @property
    def subtotal(self):
        if self.preco_unitario is None or self.quantidade is None:
            return 0
        return self.preco_unitario * self.quantidade

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome}"


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
        unique=True,
        blank=True,
        null=True
    )

    idempotency_key = models.UUIDField(
        default=uuid.uuid4,
        unique=True
    )

    qr_code = models.TextField(blank=True)
    qr_code_base64 = models.TextField(blank=True)
    boleto_url = models.TextField(blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)

    pix_expira_em = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Pagamento {self.id} - Pedido {self.pedido.id}"