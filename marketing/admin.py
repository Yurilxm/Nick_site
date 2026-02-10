from django.contrib import admin
from .models import EmailMarketing

@admin.register(EmailMarketing)
class EmailMarketingAdmin(admin.ModelAdmin):
    list_display = ('email', 'usuario', 'ativo', 'criado_em',)
    list_filter = ('ativo',)
    search_fields = ('email',)