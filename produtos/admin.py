from django.contrib import admin
from django.utils.html import format_html
from django.core.exceptions import ValidationError
from .models import Produto, Categoria, ProdutoImagem, GrupoOpcao, Opcao


# Inline para imagens do produto
class ProdutoImagemInline(admin.StackedInline):
    model = ProdutoImagem
    extra = 1

    fieldsets = (
        ('Imagem do Produto', {
            'fields': ('preview', 'imagem'),
            'description': 'Imagem que será usada no produto.'
        }),
        ('Tipo da imagem', {
            'fields': ('tipo',),
            'description': 'Escolha se esta imagem é para hover ou para detalhe do produto.'
        }),
        ('Ordem', {
            'fields': ('ordem',),
            'description': 'Defina a ordem da imagem (1, 2, 3...).'
        }),
    )

    readonly_fields = ('preview',)

    def preview(self, obj):
        if obj and obj.imagem:
            return format_html(
                '<div style="margin: 10px 0;">'
                '<img src="{}" style="width: 140px; height: 140px; '
                'object-fit: cover; border-radius: 10px; '
                'border: 2px solid #e5e7eb;" />'
                '</div>',
                obj.imagem.url
            )
        return "Nenhuma imagem selecionada"

    preview.short_description = "Preview da imagem"


# Inline para opções e grupos de opções
class OpcaoInline(admin.TabularInline):
    model = Opcao
    extra = 1


class GrupoOpcaoInline(admin.StackedInline):
    model = GrupoOpcao
    extra = 1
    inlines = [OpcaoInline]


# Admin do produto
@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    fieldsets = (
        ('🛍️ Informações do Produto', {
            'fields': ('nome', 'categoria', 'descricao', 'preco', 'imagem')
        }),
        ('⚙️ Controle', {
            'fields': ('ativo',)
        }),
        ('📅 Datas', {
            'fields': ('criado_em', 'atualizado_em')
        }),
    )

    readonly_fields = ('criado_em', 'atualizado_em', 'imagem_preview')

    list_display = (
        'imagem_preview',
        'nome',
        'categoria',
        'preco',
        'ativo',
        'criado_em',
    )

    list_filter = ('ativo', 'categoria', 'criado_em')
    search_fields = ('nome', 'descricao')
    ordering = ('-criado_em',)

    inlines = [ProdutoImagemInline, GrupoOpcaoInline]

    def imagem_preview(self, obj):
        if obj and obj.imagem:
            return format_html(
                '<img src="{}" style="width: 70px; height: 70px; '
                'object-fit: cover; border-radius: 8px; '
                'border: 1px solid #ddd;" />',
                obj.imagem.url
            )
        return "Sem imagem"

    imagem_preview.short_description = 'Capa'


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('nome',)}
    list_display = ('nome', 'slug')
    search_fields = ('nome',)
    ordering = ('nome',)