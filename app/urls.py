from django.urls import path
from .views import perfil_view, buscar_cep

urlpatterns = [
    path("perfil/", perfil_view, name="perfil"),
    path('ajax/cep/', buscar_cep, name='buscar_cep'),
]