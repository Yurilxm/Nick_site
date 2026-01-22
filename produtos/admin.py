from django.contrib import admin
from .models import Produto
from django.utils.html import format_html


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Informações do Produto', {
            'fields': ('nome', 'descricao', 'preco', 'imagem')
        }),
        ('Controle', {
            'fields': ('ativo',)
        }),
        ('Datas', {
            'fields': ('criado_em', 'atualizado_em')
        }),
    )

    readonly_fields = ('criado_em', 'atualizado_em')

    list_display = ('imagem_preview', 'nome', 'preco', 'ativo', 'criado_em')
    list_filter = ('ativo', 'criado_em')
    search_fields = ('nome', 'descricao')
    ordering = ('-criado_em',)

    def imagem_preview(self, obj):
        if obj.imagem:
            return format_html(
                '<img src="{}" style="width: 60px; border-radius: 6px;" />',
                obj.imagem.url
            )
        return "—"

    imagem_preview.short_description = 'Imagem'

