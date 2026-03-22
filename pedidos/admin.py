from django.contrib import admin
from .models import Pedido, PedidoItem, Pagamento
from produtos.models import Opcao, Categoria
from django.utils.html import format_html
from django.urls import reverse
from django.contrib.admin import SimpleListFilter
from django.utils.safestring import mark_safe


class PedidoItemInline(admin.TabularInline):
    model = PedidoItem
    extra = 0

    readonly_fields = (
        "produto",
        "quantidade",
        "preco_unitario",
        "subtotal",
        "mostrar_personalizacao",
    )

    fields = readonly_fields

    def mostrar_personalizacao(self, obj):
        if not obj.opcoes:
            return "Sem personalização"

        linhas = []
        for chave, valor in obj.opcoes.items():
            try:
                opcao = Opcao.objects.get(id=valor)
                valor_final = opcao.nome
            except:
                valor_final = valor
            linhas.append(f"<b>{chave.capitalize()}</b>: {valor_final}<br>")

        return mark_safe("".join(linhas))


class CategoriaPedidoFilter(SimpleListFilter):
    title = "Categoria do Produto"
    parameter_name = "categoria"

    def lookups(self, request, model_admin):
        categorias = Categoria.objects.all()
        return [(c.id, c.nome) for c in categorias]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                itens__produto__categoria__id=self.value()
            ).distinct()
        return queryset


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "cliente",
        "produtos",
        "status_colorido",
        "total",
        "cidade",
        "criado_em",
    )

    list_filter = (
        "status",
        "criado_em",
        "cidade",
        CategoriaPedidoFilter,
    )

    search_fields = (
        "id",
        "usuario__username",
        "usuario__email",
        "cidade",
    )

    readonly_fields = (
        "usuario",
        "total",
        "criado_em",
        "ficha_producao",
        "gerar_pdf",
    )

    actions = (
        "marcar_em_producao",
        "marcar_enviado",
        "marcar_entregue",
        "avancar_status",
    )

    inlines = [PedidoItemInline]

    def cliente(self, obj):
        return obj.usuario.username if obj.usuario else "Cliente anônimo"

    def status_colorido(self, obj):
        cores = {
            "criado": "gray",
            "aguardando_pagamento": "orange",
            "pago": "green",
            "em_producao": "blue",
            "cancelado": "red",
            "expirado": "darkred",
            "enviado": "purple",
            "entregue": "black",
        }

        cor = cores.get(obj.status, "black")

        return format_html(
            '<b style="color:{};">{}</b>',
            cor,
            obj.get_status_display()
        )

    def produtos(self, obj):
        return ", ".join(item.produto.nome for item in obj.itens.all())

    def ficha_producao(self, obj):
        cliente = obj.usuario.username if obj.usuario else "Cliente anônimo"

        linhas = []
        linhas.append(f"<h3>PEDIDO #{obj.id}</h3>")
        linhas.append(f"<b>Cliente:</b> {cliente}<br>")
        linhas.append(f"<b>CEP:</b> {obj.cep_entrega}<br>")
        linhas.append(f"<b>Endereço:</b> {obj.rua}, {obj.numero}<br>")
        linhas.append(f"<b>Bairro:</b> {obj.bairro}<br>")
        linhas.append(f"<b>Cidade:</b> {obj.cidade}/{obj.estado}<br>")
        linhas.append(f"<b>Complemento:</b> {obj.complemento}<br>")
        linhas.append("<hr><h4>Itens do pedido</h4>")

        for item in obj.itens.all():
            linhas.append(f"<b>Produto:</b> {item.produto.nome}<br>")
            linhas.append(f"<b>Quantidade:</b> {item.quantidade}<br><br>")

        return mark_safe("".join(linhas))

    def gerar_pdf(self, obj):
        url = reverse("pedidos:pedido_pdf", args=[obj.id])
        return format_html(
            '<a class="button" href="{}" target="_blank">Gerar PDF</a>',
            url
        )

    # ✅ ACTIONS SEGURAS (COM SAVE)

    def marcar_em_producao(self, request, queryset):
        for pedido in queryset:
            pedido.status = "em_producao"
            pedido.save()

    def marcar_enviado(self, request, queryset):
        for pedido in queryset:
            pedido.status = "enviado"
            pedido.save()

    def marcar_entregue(self, request, queryset):
        for pedido in queryset:
            pedido.status = "entregue"
            pedido.save()

    def avancar_status(self, request, queryset):
        for pedido in queryset:
            if pedido.status == "pago":
                pedido.status = "em_producao"
            elif pedido.status == "em_producao":
                pedido.status = "enviado"
            elif pedido.status == "enviado":
                pedido.status = "entregue"
            else:
                continue

            pedido.save()

    def changelist_view(self, request, extra_context=None):
        total = Pedido.objects.count()
        aguardando = Pedido.objects.filter(status="aguardando_pagamento").count()
        pagos = Pedido.objects.filter(status="pago").count()
        producao = Pedido.objects.filter(status="em_producao").count()
        enviados = Pedido.objects.filter(status="enviado").count()

        extra_context = extra_context or {}
        extra_context["dashboard"] = {
            "total": total,
            "aguardando": aguardando,
            "pagos": pagos,
            "producao": producao,
            "enviados": enviados,
        }

        return super().changelist_view(request, extra_context=extra_context)


@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "pedido",
        "metodo",
        "status",
        "criado_em",
    )

    list_filter = (
        "metodo",
        "status",
    )

    search_fields = (
        "transaction_id",
    )