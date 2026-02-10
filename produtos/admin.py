from django.contrib import admin
from .models import Produto, Categoria, ProdutoImagem
from django.utils.html import format_html

class ProdutoImagemInline(admin.TabularInline):
    model = ProdutoImagem
    extra = 1
    fields = ('imagem', 'ordem')

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Informações do Produto', {
            'fields': ('nome', 'categoria', 'descricao', 'preco', 'imagem')
        }),
        ('Controle', {
            'fields': ('ativo',)
        }),
        ('Datas', {
            'fields': ('criado_em', 'atualizado_em')
        }),
    )

    readonly_fields = ('criado_em', 'atualizado_em', 'imagem_preview')
    list_display = ('imagem_preview', 'nome', 'categoria', 'preco', 'ativo', 'criado_em')
    list_filter = ('ativo', 'categoria', 'criado_em')
    search_fields = ('nome', 'descricao')
    ordering = ('-criado_em',)
    inlines = [ProdutoImagemInline]

    def imagem_preview(self, obj):
        if obj.imagem:
            return format_html(
                '<img src="{}" style="width: 60px; border-radius: 6px;" />',
                obj.imagem.url
            )
        return "—"

    imagem_preview.short_description = 'Imagem'

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('nome',)}
    list_display = ('nome', 'slug')