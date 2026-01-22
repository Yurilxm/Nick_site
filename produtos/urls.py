from django.urls import path
from .views import lista_produtos, detalhe_produto

urlpatterns = [
    path('', lista_produtos, name='lista_produtos'),
    path('<int:id>/<slug:slug>/', detalhe_produto, name='detalhe_produto'),

]