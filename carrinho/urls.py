from django.urls import path
from . import views

app_name = "carrinho"

urlpatterns = [
    path('', views.ver_carrinho, name='ver_carrinho'),
    path('adicionar/<int:produto_id>/', views.adicionar_ao_carrinho, name='adicionar_ao_carrinho'),
    path('remover/<int:item_id>/', views.remover_do_carrinho, name='remover_do_carrinho'),
    path('aumentar/<int:item_id>/', views.aumentar_quantidade, name='aumentar_quantidade'),
    path('diminuir/<int:item_id>/', views.diminuir_quantidade, name='diminuir_quantidade'),
    path('mini/', views.mini_carrinho_json, name='mini_carrinho_json'),
    path("frete/calcular/", views.calcular_frete, name="calcular_frete"),
    path("frete/selecionar/", views.selecionar_frete, name="selecionar_frete"),
    path('finalizar/', views.finalizar_compra, name='finalizar_compra'),
    path("frete/limpar/", views.limpar_frete, name="limpar_frete"),
]