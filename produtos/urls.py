from django.urls import path
from .views import lista_produtos, detalhe_produto, produtos_por_categoria

urlpatterns = [
    path('', lista_produtos, name='lista_produtos'),
    path('categoria/<slug:slug>/', produtos_por_categoria, name='produtos_por_categoria'),
    path('<int:id>/<slug:slug>/', detalhe_produto, name='detalhe_produto'),
]