from django.contrib import admin
from .models import Carrinho, ItemCarrinho


class ItemCarrinhoInline(admin.TabularInline):
    model = ItemCarrinho
    extra = 0


@admin.register(Carrinho)
class CarrinhoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'ativo', 'criado_em')
    inlines = [ItemCarrinhoInline]