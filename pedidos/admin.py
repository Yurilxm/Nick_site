from django.contrib import admin
from .models import Pedido, PedidoItem


class PedidoItemInline(admin.TabularInline):
    model = PedidoItem
    extra = 0


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "usuario",
        "status",
        "total_produtos",
        "valor_frete",
        "total_geral",
        "data_criacao",
    )

    list_filter = (
        "status",
        "data_criacao",
    )

    search_fields = (
        "id",
        "usuario__username",
        "usuario__email",
    )

    inlines = [PedidoItemInline]