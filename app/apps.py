from django.apps import AppConfig


# ✅ CORRIGIDO: classe renomeada de AppConfig para AppAppConfig,
# evitando o conflito com a classe AppConfig importada do django.apps
# (que era sobrescrita antes mesmo de ser usada como classe pai).
class AppAppConfig(AppConfig):
    name = 'app'