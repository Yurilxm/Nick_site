from django.contrib import admin
from django.utils.html import format_html
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError
from django.urls import reverse
from .models import Produto, Categoria, ProdutoImagem


# 🔒 Formset para garantir apenas 1 hover
class ProdutoImagemInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()

        total_hover = 0

        for form in self.forms:
            if not hasattr(form, "cleaned_data"):
                continue

            if form.cleaned_data.get("DELETE", False):
                continue

            tipo = form.cleaned_data.get("tipo")

            if tipo == "hover":
                total_hover += 1

        if total_hover > 1:
            raise ValidationError(
                "Só é permitida uma imagem de hover por produto."
            )


class ProdutoImagemInline(admin.StackedInline):
    model = ProdutoImagem
    formset = ProdutoImagemInlineFormSet
    extra = 1

    class Media:
        js = ("admin/js/produto_imagem_inline.js",)

    fieldsets = (
        ("Imagem do Produto", {"fields": ("preview", "imagem")}),
        ("Tipo da imagem", {"fields": ("tipo",)}),
        ("Ordem", {"fields": ("ordem",)}),
    )

    readonly_fields = ("preview",)

    # 🔒 Remove opção hover se já existir
    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "tipo":
            obj_id = request.resolver_match.kwargs.get("object_id")

            if obj_id:
                produto = Produto.objects.filter(pk=obj_id).first()

                if produto and produto.tem_hover():
                    kwargs["choices"] = [
                        choice for choice in db_field.choices
                        if choice[0] != "hover"
                    ]

        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def preview(self, obj):
        if obj and obj.imagem:
            return format_html(
                '<div style="margin: 10px 0;">'
                '<img src="{}" style="width: 140px; height: 140px; '
                'object-fit: cover; border-radius: 10px; '
                'border: 2px solid #e5e7eb;" />'
                "</div>",
                obj.imagem.url,
            )
        return "Nenhuma imagem selecionada"

    preview.short_description = "Preview da imagem"


# =========================
# PRODUTO ADMIN
# =========================

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "🛍️ Informações do Produto",
            {"fields": ("nome", "categoria", "descricao", "preco", "imagem")},
        ),
        ("⚙️ Controle", {"fields": ("ativo",)}),
        ("📅 Datas", {"fields": ("criado_em", "atualizado_em")}),
    )

    readonly_fields = ("criado_em", "atualizado_em", "imagem_preview")

    list_display = (
        "imagem_preview",
        "nome",
        "categoria",
        "preco",
        "ativo",
        "criado_em",
        "edit_button",
        "delete_button",
    )

    list_filter = ("ativo", "categoria", "criado_em")
    search_fields = ("nome", "descricao")
    ordering = ("-criado_em",)

    inlines = [ProdutoImagemInline]

    def imagem_preview(self, obj):
        if obj and obj.imagem:
            return format_html(
                '<img src="{}" style="width: 70px; height: 70px; '
                'object-fit: cover; border-radius: 8px; '
                'border: 1px solid #ddd;" />',
                obj.imagem.url,
            )
        return "Sem imagem"

    imagem_preview.short_description = "Capa"

    # ✏️ BOTÃO EDITAR
    def edit_button(self, obj):
        return format_html(
            '<a style="background-color:#2563eb; color:white; '
            'padding:6px 10px; border-radius:6px; text-decoration:none;" '
            'href="{}">✏️</a>',
            reverse("admin:produtos_produto_change", args=[obj.pk])
        )

    edit_button.short_description = "Editar"

    # 🗑 BOTÃO EXCLUIR
    def delete_button(self, obj):
        return format_html(
            '<a style="background-color:#dc2626; color:white; '
            'padding:6px 10px; border-radius:6px; text-decoration:none;" '
            'href="{}">🗑</a>',
            reverse("admin:produtos_produto_delete", args=[obj.pk])
        )

    delete_button.short_description = "Excluir"


# =========================
# CATEGORIA ADMIN
# =========================

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("nome",)}

    list_display = (
        "nome",
        "slug",
        "edit_button",
        "delete_button",
    )

    search_fields = ("nome",)
    ordering = ("nome",)

    # ✏️ EDITAR
    def edit_button(self, obj):
        return format_html(
            '<a style="background-color:#2563eb; color:white; '
            'padding:6px 10px; border-radius:6px; text-decoration:none;" '
            'href="{}">✏️</a>',
            reverse("admin:produtos_categoria_change", args=[obj.pk])
        )

    edit_button.short_description = "Editar"

    # 🗑 EXCLUIR
    def delete_button(self, obj):
        return format_html(
            '<a style="background-color:#dc2626; color:white; '
            'padding:6px 10px; border-radius:6px; text-decoration:none;" '
            'href="{}">🗑</a>',
            reverse("admin:produtos_categoria_delete", args=[obj.pk])
        )

    delete_button.short_description = "Excluir"