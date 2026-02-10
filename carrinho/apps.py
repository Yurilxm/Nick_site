from django.apps import AppConfig


class CarrinhoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'carrinho'

    def ready(self):
        import carrinho.signals
