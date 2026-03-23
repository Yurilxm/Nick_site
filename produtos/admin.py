from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError
from django.urls import reverse
from .models import Produto, Categoria, ProdutoImagem, GrupoOpcao, Opcao, Avaliacao, ImagemSobre, ConfiguracaoSobre
from adminsortable2.admin import SortableAdminBase, SortableAdminMixin


# =====================================================
# BOTÕES REUTILIZÁVEIS
# =====================================================

def action_buttons(obj, app_label, model_name):
    edit_url = reverse(f"admin:{app_label}_{model_name}_change", args=[obj.pk])
    delete_url = reverse(f"admin:{app_label}_{model_name}_delete", args=[obj.pk])

    return format_html(
        '''
        <div class="action-buttons">
            <a class="btn-edit" href="{}">✏️</a>
            <a class="btn-delete" href="{}">🗑️</a>
        </div>
        ''',
        edit_url,
        delete_url
    )



# SELOS SUGESTÕES

selo_SUGESTOES = [
    "Novo",
    "Promoção",
    "Lançamento",
    "Últimas unidades",
    "Mais vendido",
    "Exclusivo",
    "Oferta especial",
    "Esgotando",
    "Destaque",
]


class SeloWidget(forms.TextInput):
    template_name = "admin/widgets/selo_produto.html"

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["selo_sugestoes"] = selo_SUGESTOES
        return context


class ProdutoAdminForm(forms.ModelForm):

    selo = forms.CharField(
        required=False,
        widget=SeloWidget()
    )

    class Meta:
        model = Produto
        fields = "__all__"


# =====================================================
# VALIDAÇÃO IMAGEM
# =====================================================

class ProdutoImagemInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        total_hover = 0

        for form in self.forms:
            if not hasattr(form, "cleaned_data"):
                continue

            if form.cleaned_data.get("DELETE", False):
                continue

            if form.cleaned_data.get("tipo") == "hover":
                total_hover += 1

        if total_hover > 1:
            raise ValidationError("Só é permitida uma imagem de hover por produto.")


class ProdutoImagemInline(admin.StackedInline):
    model = ProdutoImagem
    formset = ProdutoImagemInlineFormSet
    extra = 0
    readonly_fields = ("preview",)
    can_delete = True
    show_change_link = True


    def preview(self, obj):
        if obj and obj.imagem:
            return format_html(
                '<img src="{}" class="admin-preview-img" />',
                obj.imagem.url
            )
        return "Sem imagem"

    preview.short_description = "Preview"


class GrupoOpcaoInline(admin.StackedInline):
    model = GrupoOpcao
    extra = 0
    ordering = ("ordem",)
    show_change_link = True
    can_delete = True

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == "produto":
            field.widget.can_add_related = False
            field.widget.can_change_related = False
            field.widget.can_view_related = False
        return field


class OpcaoInline(admin.StackedInline):
    model = Opcao
    extra = 0
    ordering = ("ordem",)
    can_delete = True


# =====================================================
# PRODUTO ADMIN
# =====================================================

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):

    form = ProdutoAdminForm
    actions = None

    fieldsets = (
        ("🛍️ Informações do Produto", {
            "fields": ("nome", "categoria", "selo", "descricao", "preco", "imagem")
        }),
        ("⚙️ Controle", {
            "fields": ("ativo", "permite_personalizacao")
        }),
        ("📅 Datas", {
            "fields": ("criado_em", "atualizado_em")
        }),
    )

    readonly_fields = ("criado_em", "atualizado_em", "imagem_preview")

    list_display = (
        "imagem_preview",
        "nome",
        "categorias",
        "selo",
        "preco",
        "ativo",
        "acoes",
    )

    list_display_links = ("nome",)

    list_filter = ("ativo", "categoria")
    search_fields = ("nome",)
    ordering = ("-criado_em",)

    filter_horizontal = ("categoria",)

    inlines = [ProdutoImagemInline, GrupoOpcaoInline]

    def categorias(self, obj):
        return ", ".join([c.nome for c in obj.categoria.all()])

    def imagem_preview(self, obj):
        if obj.imagem:
            return format_html(
                '<img src="{}" class="admin-list-img" />',
                obj.imagem.url
            )
        return "—"

    imagem_preview.short_description = "Capa"

    def acoes(self, obj):
        return action_buttons(obj, "produtos", "produto")

    acoes.short_description = "Ações"

    class Media:
        css = {
            "all": ("admin/css/custom_admin.css",)
        }
        js = ("admin/js/produto_admin.js",)



# CATEGORIA
@admin.register(Categoria)
class CategoriaAdmin(SortableAdminMixin, SortableAdminBase, admin.ModelAdmin):

    actions = None

    prepopulated_fields = {"slug": ("nome",)}
    list_display = ("nome", "slug", "ordem", "acoes")
    ordering = ("ordem",)
    list_display_links = ("nome",)
    sortable_field_name = "ordem"
    exclude = ("ordem",)

    def acoes(self, obj):
        return action_buttons(obj, "produtos", "categoria")

    acoes.short_description = "Ações"


# GRUPO OPÇÔES
@admin.register(GrupoOpcao)
class GrupoOpcaoAdmin(admin.ModelAdmin):

    actions = None
    inlines = [OpcaoInline]

    list_display = (
        "nome",
        "produto",
        "tipo",
        "obrigatorio",
        "ordem",
        "acoes",
    )

    def acoes(self, obj):
        return action_buttons(obj, "produtos", "grupoopcao")

    acoes.short_description = "Ações"

    class Media:
        css = {
            "all": ("admin/css/custom_admin.css",)
        }
        js = ("admin/js/produto_admin.js",)



@admin.register(ConfiguracaoSobre)
class ConfiguracaoSobreAdmin(admin.ModelAdmin):
    readonly_fields = ("foto_preview",)

    fieldsets = (
        ("📸 Foto da Equipe / Loja", {
            "fields": ("foto_equipe", "foto_preview"),
            "description": "Aparece na seção 'Nossa história' da página Sobre."
        }),
    )

    def foto_preview(self, obj):
        if obj.foto_equipe:
            return format_html(
                '<img src="{}" class="imagem-sobre-thumb" />',
                obj.foto_equipe.url
            )
        return "Nenhuma foto cadastrada"
    foto_preview.short_description = "Preview"

    def has_add_permission(self, request):
        # Impede criar mais de um registro
        return not ConfiguracaoSobre.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    class Media:
        css = {"all": ("admin/css/custom_admin.css",)}
        js = ("admin/js/avaliacao_admin.js",)

        

# AVALIAÇÕES
@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):

    list_display = ("foto_thumb", "nome", "estrelas", "aprovado", "criado_em")
    list_filter = ("aprovado", "estrelas")
    search_fields = ("nome", "comentario")
    ordering = ("-criado_em",)
    readonly_fields = ("foto_preview",)

    fieldsets = (
        ("✍️ Avaliação", {
            "fields": ("nome", "comentario", "estrelas", "aprovado")
        }),
        ("📷 Foto", {
            "fields": ("foto", "foto_preview")
        }),
    )

    def foto_thumb(self, obj):
        if obj.foto:
            return format_html('<img src="{}" style="height:50px;border-radius:6px;" />', obj.foto.url)
        return "—"
    foto_thumb.short_description = "Foto"

    def foto_preview(self, obj):
        if obj.foto:
            return format_html(
                '<img src="{}" class="avaliacao-foto-preview" />',
                obj.foto.url
            )
        return "Nenhuma foto cadastrada"
    foto_preview.short_description = "Preview"

    class Media:
        css = {"all": ("admin/css/custom_admin.css",)}
        js = ("admin/js/avaliacao_admin.js",)


@admin.register(ImagemSobre)
class ImagemSobreAdmin(SortableAdminMixin, SortableAdminBase, admin.ModelAdmin):

    list_display = ("imagem_thumb", "ordem", "ativo", "acoes")
    ordering = ("ordem",)
    sortable_field_name = "ordem"
    readonly_fields = ("imagem_preview",)

    fieldsets = (
        ("🖼️ Imagem", {
            "fields": ("imagem", "imagem_preview", "ordem", "ativo")
        }),
    )

    def imagem_thumb(self, obj):
        if obj.imagem:
            return format_html(
                '<img src="{}" class="admin-list-img" />',
                obj.imagem.url
            )
        return "—"
    imagem_thumb.short_description = "Imagem"

    def imagem_preview(self, obj):
        if obj.imagem:
            return format_html(
                '<img src="{}" class="imagem-sobre-thumb" />',
                obj.imagem.url
            )
        return "Nenhuma imagem cadastrada"
    imagem_preview.short_description = "Preview"

    def acoes(self, obj):
        return action_buttons(obj, "produtos", "imagemsobre")
    acoes.short_description = "Ações"

    class Media:
        css = {"all": ("admin/css/custom_admin.css",)}
        js = ("admin/js/avaliacao_admin.js",)